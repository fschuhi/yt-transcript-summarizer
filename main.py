from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel
from youtube_utils import get_youtube_transcript
import openai_utils
import re
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

import colorama

colorama.init()

load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

API_KEY = os.getenv("API_KEY")  # Load from .env file
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class SummarizeRequest(BaseModel):
    video_url: str
    summary_length: int
    used_model: str


def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )


def extract_video_id(input_string: str) -> Optional[str]:
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
    timestamp = datetime.now().timestamp()
    return templates.TemplateResponse("summarizer-form.html", {"request": request, "timestamp": timestamp})


@app.post("/login")
async def login(api_key: str = Depends(get_api_key)):
    return {"access_token": api_key, "token_type": "bearer"}


@app.post("/summarize")
async def summarize(summarize_request: SummarizeRequest, api_key: str = Depends(get_api_key)):
    print("Received request:", summarize_request)

    video_id = extract_video_id(summarize_request.video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    transcript = get_youtube_transcript(video_id, include_timestamps=False)
    if not transcript:
        raise HTTPException(status_code=400, detail="Failed to retrieve transcript")

    full_text = ' '.join(transcript)
    summary = openai_utils.summarize_text(full_text, summarize_request.summary_length, summarize_request.used_model)
    word_count = len(summary.split())

    return {
        'summary': summary,
        'word_count': word_count
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)