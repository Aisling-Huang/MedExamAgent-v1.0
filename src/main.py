#!/usr/bin/env python3
"""
MedExamAgent 命令行入口
用法：python src/main.py --ppt <PPT文件> --pdf <PDF文件> [其他参数]
"""
import argparse
import os
import sys
import yaml
from pathlib import Path

from src.extractors import extract_ppt_text, extract_pdf_text
from src.search import search_web
from src.generator import generate_exam_points


def load_config(config_path: str) -> dict:
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


def parse_args():
    parser = argparse.ArgumentParser(description="🩺 MedExamAgent - 医学复习考点自动生成工具")
    parser.add_argument('--ppt', required=True, help='课程PPT文件路径 (.pptx)')
    parser.add_argument('--pdf', required=True, help='教材PDF文件路径 (.pdf)')
    parser.add_argument('--config', default='config.yaml', help='配置文件路径')
    parser.add_argument('-o', '--output', default=None, help='输出目录')
    parser.add_argument('--api-key', default=None, help='DeepSeek API Key')
    parser.add_argument('--model', default=None, help='模型名称')
    parser.add_argument('--temperature', type=float, default=None, help='温度参数(0~1)')
    parser.add_argument('--search-engine', default=None, choices=['duckduckgo', 'bing'], help='搜索引擎')
    parser.add_argument('--max-results', type=int, default=None, help='搜索条数')
    return parser.parse_args()


def main():
    args = parse_args()

    config = load_config(args.config)

    api_key = args.api_key or os.getenv('DEEPSEEK_API_KEY') or \
              config.get('deepseek', {}).get('api_key')
    if not api_key:
        print("❌ 未提供 DeepSeek API Key。可通过 --api-key、环境变量或配置文件提供。")
        sys.exit(1)

    base_url = config.get('deepseek', {}).get('base_url', 'https://api.deepseek.com')
    model = args.model or config.get('deepseek', {}).get('model', 'deepseek-chat')
    temperature = args.temperature if args.temperature is not None else \
                  config.get('deepseek', {}).get('temperature', 0.3)

    search_engine = args.search_engine or config.get('search', {}).get('engine', 'duckduckgo')
    max_results = args.max_results or config.get('search', {}).get('max_results', 3)

    output_dir = args.output or config.get('output', {}).get('save_path', './output')
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("📖 提取PPT文本...")
    slides = extract_ppt_text(args.ppt)
    print(f"   ✓ {len(slides)} 页")

    print("📖 提取PDF教材文本...")
    pages = extract_pdf_text(args.pdf)
    print(f"   ✓ {len(pages)} 页")

    sections = [(i+1, slides[i], pages[i] if i < len(pages) else "") for i in range(len(slides))]
    total = len(sections)
    print(f"🔗 共 {total} 节，开始生成...\n")

    all_results = []
    for num, slide, pdf in sections:
        print(f"⚙️  处理 第{num}/{total} 节...")
        combined = f"【PPT内容】\n{slide}\n\n【教材参考】\n{pdf}"
        query = ' '.join(slide.split()[:20]) + " 医学 考点"

        try:
            search_res = search_web(query, engine=search_engine, max_results=max_results)
            print(f"   🔍 搜索完成，{len(search_res)} 条补充")
        except Exception as e:
            print(f"   ⚠️  搜索失败: {e}")
            search_res = []

        try:
            content = generate_exam_points(
                section_title=f"第{num}节",
                section_text=combined,
                search_results=search_res,
                api_key=api_key,
                base_url=base_url,
                model=model,
                temperature=temperature
            )
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
            content = f"## 第{num}节 - 生成失败\n\n错误信息: {e}"

        all_results.append(content)

        out_file = Path(output_dir) / f"section_{num:02d}.md"
        out_file.write_text(content, encoding='utf-8')
        print(f"   💾 已保存 {out_file}\n")

    if total > 1:
        combined_path = Path(output_dir) / "all_sections.md"
        combined_path.write_text("\n\n---\n\n".join(all_results), encoding='utf-8')
        print(f"📚 汇总文件: {combined_path}")

    print("\n✅ 全部完成！")


if __name__ == '__main__':
    main()