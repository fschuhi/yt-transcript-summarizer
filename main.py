from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_utils import get_youtube_data
import openai_utils
import re
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv
import logging
from functools import lru_cache
import colorama
from auth_utils import hash_password, verify_password, create_access_token
from user_data import get_user, add_user
# noinspection PyPackageRequirements
from jose import JWTError, jwt


colorama.init()

load_dotenv()

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://vue.fschuhi.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and logging setup (unchanged)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class SummarizeRequest(BaseModel):
    video_url: str
    summary_length: int
    used_model: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


@lru_cache()
def get_secret_key():
    return os.getenv("SECRET_KEY")


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return username  # Return just the username


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
    """
    Render the summarizer form template with current timestamp.

    :param request: The incoming request
    :return: TemplateResponse with the summarizer form
    """
    # 09.08.24 doesn't work anymore, because we've changed to JWT auth and using username/password instead of "API key"
    logger.info("Received request for root endpoint")
    timestamp = datetime.now().timestamp()
    return templates.TemplateResponse("summarizer-form.html", {"request": request, "timestamp": timestamp})


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint hit")
    return {"status": "healthy"}


@app.post("/register")
async def register(user: UserCreate):
    logger.info(f"Received registration request: {user.username}, {user.email}")
    if get_user(user.username):
        logger.warning(f"Username already registered: {user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    add_user(user.username, user.email, hashed_password)
    logger.info(f"User registered successfully: {user.username}")
    return {"message": "User registered successfully"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt received for user: {form_data.username}")
    try:
        user = get_user(form_data.username)
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if not verify_password(form_data.password, user['password']):
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        logger.info(f"Login successful for user: {form_data.username}")
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@app.post("/summarize")
async def summarize(summarize_request: SummarizeRequest, current_user: str = Depends(get_current_user)):
    logger.info(f"Received summarize request from user: {current_user}")

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
