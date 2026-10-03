"""
This module contains common utility functions.
"""

import re

def strip_text(text : str) -> str:
    """
    Return just the score string from post text. This provides a simple,
    one-liner to represent the post.
    """
    result  : str = ""
    pattern : str = r"^[A-Z]{3}: \d{1,2} \| [A-Z]{3}: \d{1,2}$"
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        result = match.group(0).strip()
    return result
