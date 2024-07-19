# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.types import Scope
from pydantic import BaseModel
from youtube_utils import get_youtube_transcript
import openai_utils
import re
from datetime import datetime
from typing import Optional

import colorama
colorama.init()

app = FastAPI()


# not needed because we use StaticFiles()
class CustomStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        if path.endswith('.js'):
            response.headers['Cache-Control'] = 'no-cache, max-age=0'
        else:
            response.headers['Cache-Control'] = 'public, max-age=3600'
        return response


# Mount static files
# app.mount("/static", CustomStaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")


class SummarizeRequest(BaseModel):
    video_url: str
    summary_length: int
    used_model: str


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


@app.post("/summarize")
async def summarize(summarize_request: SummarizeRequest):
    print("Received request:", summarize_request)
    # ... rest of the function remains the same

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
