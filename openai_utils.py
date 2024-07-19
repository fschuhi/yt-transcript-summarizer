# openai_utils.py
import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def word_count(s):
    return len(re.findall(r'\w+', s))


def summarize_text(text: str, max_words: int, used_model: str = "gpt-3.5-turbo") -> str:
    """
    Summarize the given text using OpenAI's API.

    :param text: The text to summarize
    :param max_words: The approximate maximum number of words for the summary
    :param used_model: The name of the model to use, default: "gpt-3.5-turbo"
    :return: The summarized text
    """
    try:
        response = client.chat.completions.create(
            model=used_model,
            messages=[
                {"role": "system",
                 "content": f"You are a helpful assistant that summarizes text. Please summarize the following text "
                            f"in approximately {max_words} words. It's important that your summary has at least "
                            f"{max_words} words, but it also shouldn't have a word count that is significantly higher "
                            f"than {max_words}."},
                {"role": "user", "content": "Summarize this text: " + text}
            ],
            max_tokens=max_words * 4,  # A rough estimate, as tokens != words
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"An error occurred while summarizing: {str(e)}")
        return ""
