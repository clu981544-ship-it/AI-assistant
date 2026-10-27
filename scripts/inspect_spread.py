import pdfplumber
import json
import re
from inspect_rules import PROJECT_ROOT,SOURCE_PATH
FOOTER_HEIGHT=40
RULE_VERSION="2026/27"
OUTPUT_PATH=(
    PROJECT_ROOT
    /"knowledge_base"
    / "processed"
    / "rules-2026-27-sample.jsonl"
)
def parse_printed_page(footer_text: str) -> int | None:
    remaining = re.sub(r"\bLaw\s+\d+\b", "", footer_text)

    candidates = [
        part
        for part in remaining.split()
        if part.isdecimal()
    ]

    if len(candidates) != 1:
        return None

    return int(candidates[0])
def parse_law_metadata(footer_text: str) -> tuple[int | None, str | None]:
    match = re.search(
        r"\|\s*Law\s+(\d+)\s*\|\s*(.+)",
        footer_text,
    )

    if match is None:
        return None, None

    law_number = int(match.group(1))
    law_title = match.group(2).strip()

    printed_page = parse_printed_page(footer_text)
    if printed_page is not None:
        law_title = law_title.removesuffix(f" {printed_page}").strip()

    return law_number, law_title
def main():
    records=[]

    with pdfplumber.open(SOURCE_PATH) as pdf:
        pdf_page = 56
        page = pdf.pages[pdf_page - 1]
        middle = page.width / 2

        regions = {
            "left": (0, 0, middle, page.height),
            "right": (middle, 0, page.width, page.height),
        }

        for side, bbox in regions.items():
            half_page = page.crop(bbox)
            left, top, right, bottom = bbox
            footer_top = page.height - FOOTER_HEIGHT

            body = half_page.crop((left, top, right, footer_top))
            footer = half_page.crop((left, footer_top, right, bottom))

            body_text = body.extract_text(use_text_flow=True) or ""
            footer_text = footer.extract_text(use_text_flow=True) or ""
            law_number, law_title = parse_law_metadata(footer_text)
            records.append({
                "source_file": SOURCE_PATH.relative_to(PROJECT_ROOT).as_posix(),
                "rule_version": RULE_VERSION,
                "pdf_page": pdf_page,
                "side": side,
                "printed_page": parse_printed_page(footer_text),
                "law_number": law_number,
                "law_title": law_title,
                "footer_height": FOOTER_HEIGHT,
                "footer_text": footer_text,
                "text": body_text,
            })
            print(f"\n===== PDF 第 {pdf_page} 页 / {side} =====")
            print("【页脚】")
            print(footer_text)
            print("【正文】")
            print(body_text)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as output:
        for record in records:
            line = json.dumps(record, ensure_ascii=False)
            output.write(line + "\n")

    print(f"\n已保存 {len(records)} 条记录：{OUTPUT_PATH}")
if __name__ == "__main__":
    main()
