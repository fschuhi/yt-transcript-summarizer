import re
from typing import Optional


def extract_video_id(input_string: str) -> Optional[str]:
    """Extract the YouTube video ID from various URL formats or direct ID input.

    Args:
        input_string: The input string containing a YouTube URL or video ID.
    Returns: The extracted video ID, or None if no valid ID is found.
    """
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)

    if re.match(r"^[a-zA-Z0-9_-]{11}$", input_string):
        return input_string

    return None


def word_count(s: str) -> int:
    """Count words in a string using regex.

    Args:
        s: Input string to count words from.
    Returns: Number of words in the input string.
    """
    return len(re.findall(r"\w+", s))
