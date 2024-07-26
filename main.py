from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_utils import get_youtube_data
import openai_utils
import re
from datetime import datetime
from typing import Optional
from typing import cast
import os
from dotenv import load_dotenv
import logging
from functools import lru_cache

import colorama

colorama.init()

load_dotenv()

app = FastAPI()

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://vue.fschuhi.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class SummarizeRequest(BaseModel):
    video_url: str
    summary_length: int
    used_model: str


@lru_cache()
def get_api_key_value():
    return os.getenv("API_KEY")


def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Dependency function to validate the API key, using FastAPI's Depends.

    :param api_key: The API key to validate
    :return: The API key if valid
    :raises HTTPException: 403 Forbidden if the API key is invalid
    """
    if api_key == get_api_key_value():
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
async def summarize(summarize_request: SummarizeRequest, _api_key: str = Depends(get_api_key)):
    """
    Summarize YouTube video with ChatGPT.

    :param summarize_request: The request body containing video URL and summary parameters
    :param _api_key: The API key for authentication, not used for the request, but necessary for dependency injection
    :return: A dictionary with the summary, word count, and YouTube metadata
    :raises HTTPException: 400 Bad Request if the YouTube URL is invalid or transcript retrieval fails
    """
    logger.info(f"Received summarize request: {summarize_request}")

    try:
        video_id = extract_video_id(summarize_request.video_url)
        if not video_id:
            logger.error(f"Invalid YouTube URL: {summarize_request.video_url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        logger.info(f"Extracted video ID: {video_id}")
        youtube_data = get_youtube_data(video_id)

        if not youtube_data['transcript']:
            logger.error(f"Failed to retrieve transcript for video ID: {video_id}")
            raise HTTPException(status_code=400, detail="Failed to retrieve transcript")

        full_text = ' '.join(youtube_data['transcript'])
        logger.info(f"Transcript retrieved. Length: {len(full_text)} characters")

        summary = openai_utils.summarize_text(full_text, youtube_data['metadata'], summarize_request.summary_length,
                                              summarize_request.used_model)
        logger.info(f"Summary generated. Length: {len(summary)} characters")

        word_count = len(summary.split())

        return {
            'summary': summary,
            'word_count': word_count,
            'metadata': youtube_data['metadata']
        }
    except Exception as e:
        logger.exception(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
