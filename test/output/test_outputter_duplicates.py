"""
Unit tests for scoreline-based duplicate matching in Outputter.
"""

import unittest

from src.output.printer import Printer


class TestOutputterDuplicateMatching(unittest.TestCase):
    def test_has_posted_matches_by_scoreline_text(self):
        outputter = Printer()
        outputter.add_post(
            "Colorado goal!\n\nScored by Someone.\n\nCOL: 4 | MIN: 3\n\n#GoAvsGo"
        )

        query = "Minnesota goal!\n\nScored by Another Player.\n\nCOL: 4 | MIN: 3\n\n#mnwild"

        self.assertTrue(outputter.has_posted(query))

    def test_has_posted_today_falls_back_to_full_text_when_no_scoreline(self):
        outputter = Printer()
        outputter.add_post("General status post without scoreline")

        self.assertTrue(outputter.has_posted_today("General status post without scoreline"))
        self.assertFalse(outputter.has_posted_today("Different status post"))


if __name__ == "__main__":
    unittest.main()
