"""
Unit tests for utility helpers in `src.utils`.
"""

import unittest

from src.utils import strip_text


class TestUtils(unittest.TestCase):
    """
    Tests for `strip_text` behavior with matching and non-matching input.
    """

    def test_strip_text_matches_block(self):
        """
        When the text contains a score line, it is returned.
        """
        text = "Header\nCOL: 3 | DET: 2\nFooter"
        result = strip_text(text)
        self.assertEqual(result, "COL: 3 | DET: 2")

    def test_strip_text_no_match(self):
        """
        If no score line exists, empty string is returned.
        """
        text = "No scores here"
        result = strip_text(text)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
