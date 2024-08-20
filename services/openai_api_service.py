"""Implementation of OpenAI service for text summarization."""

import os
from dotenv import load_dotenv
from openai import OpenAI
from services.service_interfaces import IOpenAIAPIService

load_dotenv()


class OpenAIAPIService(IOpenAIAPIService):
    """OpenAI service for text summarization."""

    def __init__(self, client: OpenAI = None):
        """Initialize the OpenAI service."""
        self._client = client or self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI client, using the API key from environment.

        Raises: ValueError if OPENAI_API_KEY is not set.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self._client = OpenAI(api_key=api_key)

    def summarize_text(self, text: str, metadata: dict, max_words: int, used_model: str = "gpt-3.5-turbo") -> str:
        """Summarize given text using OpenAI's API, incorporating video metadata.

        Args:
            text: The transcript text to summarize.
            metadata: Dict containing video metadata (title, channel, etc.).
            max_words: Target word count for the summary.
            used_model: OpenAI model to use (default: gpt-3.5-turbo).
        Returns: Summarized text or empty string if an error occurs.
        """
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
            response = self._client.chat.completions.create(
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
