import os
import tempfile
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.extractors import extract_ppt_text, extract_pdf_text
from src.generator import generate_exam_points
from src.utils import smart_match, extract_pdf_outline, extract_chapters_from_text

# ---------- 日志 ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medexam")

app = FastAPI(title="MedExamAgent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 40 * 1024 * 1024   # 40MB
ALLOWED_EXTENSIONS = ('.pptx', '.pdf')

@app.post("/generate")
async def generate(
    ppt: List[UploadFile] = File(...),
    pdf: UploadFile = File(...),
    api_key: str = Form(...),
    model: str = Form("deepseek-chat"),
    temperature: float = Form(0.2),
    search_engine: str = Form("baidu"),   # 参数保留，但已不使用
    max_results: int = Form(5)
):
    # ---- 文件校验 ----
    if not ppt or len(ppt) == 0:
        return JSONResponse({"status": "error", "message": "至少需要上传一个 PPT/PDF 讲义文件"}, status_code=400)

    for p in ppt:
        if not p.filename or not p.filename.lower().endswith(ALLOWED_EXTENSIONS):
            return JSONResponse({
                "status": "error",
                "message": f"文件 {p.filename} 格式错误，仅支持 .pptx 和 .pdf"
            }, status_code=400)

    if not pdf.filename or not pdf.filename.lower().endswith('.pdf'):
        return JSONResponse({"status": "error", "message": "教材 PDF 文件格式错误，仅支持 .pdf"}, status_code=400)

    # 读取教材 PDF
    pdf_bytes = await pdf.read()
    if len(pdf_bytes) > MAX_FILE_SIZE:
        return JSONResponse({"status": "error", "message": "教材文件大小超过 40MB 限制"}, status_code=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf.write(pdf_bytes)
        pdf_path = tmp_pdf.name

    # 提取教材文本
    try:
        pdf_pages = extract_pdf_text(pdf_path)
    except Exception as e:
        logger.error(f"教材提取失败: {e}")
        return JSONResponse({"status": "error", "message": "教材提取失败，请检查文件"}, status_code=500)

    # 提取教材大纲/章节
    outline = extract_pdf_outline(pdf_path)
    chapters = extract_chapters_from_text(pdf_pages) if not outline else []

    results = []

    try:
        for p in ppt:
            ppt_bytes = await p.read()
            if len(ppt_bytes) > MAX_FILE_SIZE:
                logger.warning(f"跳过超大文件: {p.filename}")
                continue

            # 确定文件后缀
            ext = os.path.splitext(p.filename)[1].lower()
            suffix = ext if ext else ".pptx"  # 默认 .pptx

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_ppt:
                tmp_ppt.write(ppt_bytes)
                ppt_path = tmp_ppt.name

            try:
                # 根据文件类型提取文本
                if ext == '.pdf':
                    # PDF 讲义：提取所有页文本，合并为一个章节内容
                    slides = extract_pdf_text(ppt_path)
                    ppt_full_text = "\n".join(slides) if slides else ""
                else:
                    # .pptx 文件
                    slides = extract_ppt_text(ppt_path)
                    ppt_full_text = "\n".join(slides) if slides else ""

                if not ppt_full_text.strip():
                    logger.warning(f"文件 {p.filename} 未提取到任何文本")
                    continue

                # 章节标题：文件名（不含扩展名）
                chapter_title = os.path.splitext(p.filename or "未命名")[0]

                # 智能匹配教材对应章节
                matched_pdf = smart_match(ppt_full_text, pdf_pages, outline, chapters)

                # 永久关闭联网搜索
                search_res = []

                # 构建上下文
                combined_context = f"【PPT内容】\n{ppt_full_text}\n\n【教材参考】\n{matched_pdf}"

                # 生成考点
                content = generate_exam_points(
                    section_title=chapter_title,
                    section_text=combined_context,
                    search_results=search_res,
                    api_key=api_key,
                    base_url="https://api.deepseek.com",
                    model=model,
                    temperature=temperature
                )
                results.append({"section": chapter_title, "content": content})

            except Exception as e:
                logger.error(f"处理文件 {p.filename} 失败: {e}")
                results.append({
                    "section": os.path.splitext(p.filename or "未知")[0],
                    "content": f"## 生成失败\n\n服务器内部错误，请稍后重试。"
                })
            finally:
                if os.path.exists(ppt_path):
                    os.unlink(ppt_path)

    except Exception as e:
        logger.error(f"全局异常: {e}")
        return JSONResponse({"status": "error", "message": "服务器内部错误"}, status_code=500)
    finally:
        if os.path.exists(pdf_path):
            os.unlink(pdf_path)

    return JSONResponse({"status": "ok", "data": results})