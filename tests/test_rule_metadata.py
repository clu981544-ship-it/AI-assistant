"""页脚元数据回归测试，不访问模型、网络或数据库。"""

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from inspect_spread import parse_law_metadata, parse_printed_page


class RuleMetadataTests(unittest.TestCase):
    def test_repeated_page_numbers_are_not_ambiguous(self):
        for footer, expected in [("51 51", 51), ("91\n91", 91), ("104 104", 104)]:
            with self.subTest(footer=footer):
                self.assertEqual(parse_printed_page(footer), expected)

    def test_conflicting_page_numbers_remain_unresolved(self):
        for footer in ["51 52", "104 104 105"]:
            with self.subTest(footer=footer):
                self.assertIsNone(parse_printed_page(footer))

    def test_version_and_law_number_are_not_printed_pages(self):
        footer = "Laws of the Game 2026/27 | Law 11 | Offside"
        self.assertIsNone(parse_printed_page(footer))
        self.assertEqual(parse_printed_page(footer + " 111"), 111)
        self.assertEqual(parse_law_metadata(footer + " 111"), (11, "Offside"))

    def test_empty_footer_preserves_unknown_metadata(self):
        self.assertIsNone(parse_printed_page(""))
        self.assertEqual(parse_law_metadata(""), (None, None))


if __name__ == "__main__":
    unittest.main()
