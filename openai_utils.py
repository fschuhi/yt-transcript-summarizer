# openai_utils.py
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

_client = None


def get_openai_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client = OpenAI(api_key=api_key)
    return _client


def word_count(s):
    return len(re.findall(r'\w+', s))


def summarize_text(text: str, metadata: dict, max_words: int, used_model: str = "gpt-3.5-turbo") -> str:
    client = get_openai_client()
    try:
        # Prepare the metadata string
        metadata_str = f"""
        Title: {metadata['title']}
        Channel: {metadata['channel_title']}
        Published: {metadata['publish_date']}
        Views: {metadata['view_count']}
        Likes: {metadata['like_count']}
        Comments: {metadata['comment_count']}
        Description: {metadata['description']}
        """

        response = client.chat.completions.create(
            model=used_model,
            messages=[
                {"role": "system",
                 "content": f"You are a helpful assistant that summarizes YouTube videos. Please summarize the "
                            f"following video transcript in approximately {max_words} words. Use the provided metadata "
                            f"to enhance your summary. It's important that your summary has at least {max_words} "
                            f"words, but it also shouldn't have a word count that is significantly higher than "
                            f"{max_words}."},
                {"role": "user",
                 "content": f"Here's the video metadata:\n{metadata_str}\n\nNow, summarize this transcript: {text}"}
            ],
            max_tokens=max_words * 4,  # A rough estimate, as tokens != words
            n=1,
            stop=None,
            temperature=0.7,
        )
        summary = response.choices[0].message.content.strip()

        return summary
    except Exception as e:
        print(f"An error occurred while summarizing: {str(e)}")
        return ""
