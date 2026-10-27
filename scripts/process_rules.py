import json

import pdfplumber

from inspect_rules import PROJECT_ROOT, SOURCE_PATH
from inspect_spread import parse_law_metadata, parse_printed_page


START_PAGE = 23
END_PAGE = 76
OUTPUT_PATH = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
    / "rules-2026-27-pages.jsonl"
)


def is_footer(obj: dict, height: float) -> bool:
    return (
        obj.get("object_type") == "char"
        and 5.5 <= obj.get("size", 0) <= 6.5
        and height - 31 <= obj.get("top", -1) <= height - 22
    )


def main():
    records = []
    current_law = (None, None)

    with pdfplumber.open(SOURCE_PATH) as pdf:
        for pdf_page in range(START_PAGE, END_PAGE + 1):
            page = pdf.pages[pdf_page - 1]

            if page.width <= page.height:
                raise ValueError(f"第 {pdf_page} 页不是预期的横向双页")

            middle = page.width / 2
            regions = {
                "left": (0, 0, middle, page.height),
                "right": (middle, 0, page.width, page.height),
            }

            for side, bbox in regions.items():
                half = page.crop(bbox)

                footer = half.filter(
                    lambda obj: is_footer(obj, page.height)
                )
                body = half.filter(
                    lambda obj: not is_footer(obj, page.height)
                )

                footer_text = footer.extract_text(use_text_flow=True) or ""
                text = body.extract_text(use_text_flow=True) or ""

                printed_page = parse_printed_page(footer_text)
                law_number, law_title = parse_law_metadata(footer_text)

                if law_number is not None:
                    current_law = (law_number, law_title)
                    law_source = "footer"
                elif printed_page is not None and current_law[0] is not None:
                    law_number, law_title = current_law
                    law_source = "previous_footer"
                else:
                    law_source = "unresolved"

                review_reasons = []
                if printed_page is None:
                    review_reasons.append("missing_printed_page")
                if not text.strip():
                    review_reasons.append("empty_text")

                records.append({
                    "source_file": SOURCE_PATH.relative_to(PROJECT_ROOT).as_posix(),
                    "rule_version": "2026/27",
                    "pdf_page": pdf_page,
                    "side": side,
                    "printed_page": printed_page,
                    "law_number": law_number,
                    "law_title": law_title,
                    "law_source": law_source,
                    "extraction_mode": "text_only",
                    "review_reasons": review_reasons,
                    "footer_text": footer_text,
                    "text": text,
                })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"保存记录：{len(records)}")
    print(f"未解析页码：{sum(r['printed_page'] is None for r in records)}")
    print(f"无正文区域：{sum(not r['text'].strip() for r in records)}")
    print(f"输出文件：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()