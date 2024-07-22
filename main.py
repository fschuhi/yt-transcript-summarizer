from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel
from youtube_utils import get_youtube_data
import openai_utils
import re
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
import logging

import colorama

colorama.init()

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Access the logger
logger = logging.getLogger(__name__)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("API_KEY")  # Load from .env file
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class SummarizeRequest(BaseModel):
    video_url: str
    summary_length: int
    used_model: str


def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Dependency function to validate the API key, using FastAPI's Depends.

    :param api_key: The API key to validate
    :return: The API key if valid
    :raises HTTPException: 403 Forbidden if the API key is invalid
    """
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )


def extract_video_id(input_string: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL or video ID string.

    :param input_string: The input URL or video ID string
    :return: The extracted video ID, or None if invalid
    """
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)

    if re.match(r'^[a-zA-Z0-9_-]{11}$', input_string):
        return input_string

    return None


@app.get("/")
async def read_root(request: Request):
    """
    Render the summarizer form template with current timestamp.

    :param request: The incoming request
    :return: TemplateResponse with the summarizer form
    """
    logger.info("Received request for root endpoint")
    timestamp = datetime.now().timestamp()
    return templates.TemplateResponse("summarizer-form.html", {"request": request, "timestamp": timestamp})


@app.get("/health")
async def health_check():
    """
    Return the health status of the application, called by AWS.

    :return: A dictionary with the status
    """
    return {"status": "healthy"}


@app.post("/login")
async def login(api_key: str = Depends(get_api_key)):
    """
    Validate API key using the get_api_key dependency and return access token if valid.

    :param api_key: The API key to validate
    :return: A dictionary with the access token and token type
    """
    return {"access_token": api_key, "token_type": "bearer"}


@app.post("/summarize")
async def summarize(summarize_request: SummarizeRequest, api_key: str = Depends(get_api_key)):
    """
    Summarize YouTube video with ChatGPT.

    :param summarize_request: The request body containing video URL and summary parameters
    :param api_key: The API key for authentication
    :return: A dictionary with the summary, word count, and YouTube metadata
    :raises HTTPException: 400 Bad Request if the YouTube URL is invalid or transcript retrieval fails
    """
    logger.info(f"Received summarize request: {summarize_request}")

    video_id = extract_video_id(summarize_request.video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    youtube_data = get_youtube_data(video_id)
    if not youtube_data['transcript']:
        raise HTTPException(status_code=400, detail="Failed to retrieve transcript")

    full_text = ' '.join(youtube_data['transcript'])
    summary = openai_utils.summarize_text(full_text, youtube_data['metadata'], summarize_request.summary_length,
                                          summarize_request.used_model)
    word_count = len(summary.split())

    return {
        'summary': summary,
        'word_count': word_count,
        'metadata': youtube_data['metadata']
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)