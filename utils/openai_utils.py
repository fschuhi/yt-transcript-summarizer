"""Utilities for interacting with OpenAI's API and text summarization."""

import os
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None


def get_openai_client():
    """Initialize and return the OpenAI client, using the API key from environment.

    Returns: Initialized OpenAI client.
    Raises: ValueError if OPENAI_API_KEY is not set.
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


def word_count(s: str) -> int:
    """Count words in a string using regex.

    Args:
        s: Input string to count words from.
    Returns: Number of words in the input string.
    """
    return len(re.findall(r"\w+", s))


def summarize_text(text: str, metadata: dict, max_words: int, used_model: str = "gpt-3.5-turbo") -> str:
    """Summarize given text using OpenAI's API, incorporating video metadata.

    Args:
        text: The transcript text to summarize.
        metadata: Dict containing video metadata (title, channel, etc.).
        max_words: Target word count for the summary.
        used_model: OpenAI model to use (default: gpt-3.5-turbo).
    Returns: Summarized text or empty string if an error occurs.
    """
    client = get_openai_client()
    try:
        # Construct metadata string for context
        metadata_str = f"""
        Title: {metadata['title']}
        Channel: {metadata['channel_title']}
        Published: {metadata['publish_date']}
        Views: {metadata['view_count']}
        Likes: {metadata['like_count']}
        Comments: {metadata['comment_count']}
        Description: {metadata['description']}
        """

        # Create chat completion request
        response = client.chat.completions.create(
            model=used_model,
            messages=[
                {
                    "role": "system",
                    "content": f"Summarize the following YouTube video transcript in ~{max_words} words. "
                               f"Use the provided metadata to enhance your summary. Aim for at least {max_words} "
                               f"words, but not significantly more.",
                },
                {
                    "role": "user",
                    "content": f"Video metadata:\n{metadata_str}\n\nTranscript: {text}",
                },
            ],
            max_tokens=max_words * 4,  # Rough estimate: tokens != words
            n=1,
            stop=None,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summarization error: {str(e)}")
        return ""
