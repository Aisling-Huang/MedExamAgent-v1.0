import re
import logging
from PyPDF2 import PdfReader
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("medexam.utils")

# ---------- 基础文本清洗 ----------
def preprocess_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    return text

# ---------- TF-IDF 匹配 (回退方案) ----------
def match_ppt_to_pdf(pdf_pages: list[str], ppt_slide_text: str, top_k: int = 3) -> str:
    """为单张 PPT 找到最相关的 PDF 页，返回拼接文本"""
    if not pdf_pages or not ppt_slide_text.strip():
        return ""

    clean_pdf = [preprocess_text(p) for p in pdf_pages]
    clean_ppt = preprocess_text(ppt_slide_text)

    vectorizer = TfidfVectorizer(max_features=5000)
    all_texts = clean_pdf + [clean_ppt]
    tfidf = vectorizer.fit_transform(all_texts)
    pdf_vecs = tfidf[:-1]
    ppt_vec = tfidf[-1]

    sims = cosine_similarity(ppt_vec, pdf_vecs).flatten()
    top_indices = sims.argsort()[-top_k:][::-1]
    top_indices_sorted = sorted(top_indices)
    return "\n\n".join([pdf_pages[i] for i in top_indices_sorted])

# ---------- 大纲提取 ----------
def extract_pdf_outline(pdf_path: str) -> list[dict]:
    """提取 PDF 书签，返回 [{'title':str, 'page':int(从0开始)}]"""
    try:
        reader = PdfReader(pdf_path)
        outlines = reader.outline
        if not outlines:
            return []
        result = []
        def recurse(items):
            for item in items:
                if isinstance(item, list):
                    recurse(item)
                else:
                    title = item.title
                    page_num = reader.get_destination_page_number(item)
                    result.append({"title": title, "page": page_num})
        recurse(outlines)
        return result
    except Exception as e:
        logger.warning(f"大纲提取失败: {e}")
        return []

def extract_chapters_from_text(pages: list[str]) -> list[dict]:
    """通过正则匹配'第X章'等模式，返回 [{'title':str, 'page':int}]"""
    chapters = []
    # 匹配常见的章节标题模式
    patterns = [
        r'第[一二三四五六七八九十百千\d]+\s*章',
        r'Chapter\s+\d+',
        r'第[一二三四五六七八九十百千\d]+\s*节',
    ]
    for i, page_text in enumerate(pages):
        for pat in patterns:
            match = re.search(pat, page_text)
            if match:
                title = match.group()
                chapters.append({"title": title, "page": i})
                break  # 一页只取一个标题
    return chapters

# ---------- 智能章节匹配 ----------
def match_ppt_to_chapter(ppt_text: str, chapters: list[dict], pages: list[str]) -> str:
    """将 PPT 文本匹配到最近的章节，返回该章节的连续页面文本"""
    if not chapters:
        return ""
    # 简单的关键词匹配：统计PPT和章节标题的公共词
    ppt_words = set(preprocess_text(ppt_text).split())
    best_chapter = None
    best_score = 0
    for ch in chapters:
        ch_words = set(preprocess_text(ch["title"]).split())
        score = len(ppt_words & ch_words)
        if score > best_score:
            best_score = score
            best_chapter = ch
    if not best_chapter:
        return ""
    # 找到该章节的结束页码（下一个章节开始前）
    start_idx = best_chapter["page"]
    end_idx = len(pages)
    for ch in chapters:
        if ch["page"] > start_idx:
            end_idx = ch["page"]
            break
    # 返回该章节全部页（最多取10页，避免过长）
    chapter_pages = pages[start_idx:min(end_idx, start_idx+10)]
    return "\n\n".join(chapter_pages)

def smart_match(ppt_text: str, pdf_pages: list[str], outline: list[dict], chapters: list[dict]) -> str:
    """
    智能匹配：大纲 > 文字章节 > TF-IDF
    返回匹配后的教材文本段落
    """
    # 1. 优先用书签大纲
    if outline:
        matched = match_ppt_to_chapter(ppt_text, outline, pdf_pages)
        if matched:
            return matched
    # 2. 其次用文字章节
    if chapters:
        matched = match_ppt_to_chapter(ppt_text, chapters, pdf_pages)
        if matched:
            return matched
    # 3. 回退 TF-IDF
    return match_ppt_to_pdf(pdf_pages, ppt_text, top_k=3)