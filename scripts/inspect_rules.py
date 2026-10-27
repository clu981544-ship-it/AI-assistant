from pathlib import Path

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = (
    PROJECT_ROOT
    / "knowledge_base"
    / "documents"
    / "Laws of the Game 2026_27_double pages.pdf"
)


def main():
    reader = PdfReader(SOURCE_PATH)
    pdf_page = 56
    page = reader.pages[pdf_page - 1]
    text = page.extract_text() or ""

    print("来源文件：", SOURCE_PATH.name)
    print("PDF 总页数：", len(reader.pages))
    print("PDF 页码：", pdf_page)
    print("页面宽度：", float(page.mediabox.width))
    print("页面高度：", float(page.mediabox.height))
    print("提取文字数：", len(text))
    print("----- 原始提取文本 -----")
    print(text)


if __name__ == "__main__":
    main()
