import colorama
from dotenv import load_dotenv
from functools import lru_cache
import logging
import os
from pydantic import BaseModel
import re
import sys
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from repositories.repository_provider import get_repository
from services.service_interfaces import IUserRepository
from services.user_auth_service import UserAuthService

# do not change, used in test_summarize_endpoint_authorized for @patch
from utils.youtube_utils import get_youtube_data
from utils import openai_utils

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
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    repo: IUserRepository = Depends(get_repository)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_auth_service = UserAuthService(repo)
    try:
        user = user_auth_service.authenticate_user_by_token(token)
        if user is None:
            raise credentials_exception
        return user.user_name
    except Exception:
        raise credentials_exception


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
    Forbid access to the root endpoint.

    This endpoint is no longer accessible due to changes in authentication method
    and overall API structure. It now returns a 403 Forbidden response.

    :param request: The incoming request
    :raises HTTPException: Always raises a 403 Forbidden exception
    """
    logger.info("Received request for root endpoint (forbidden)")
    raise HTTPException(status_code=403, detail="Access to this endpoint is forbidden")


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint hit")
    return {"status": "healthy"}


@app.post("/register")
async def register(user: UserCreate, repo: IUserRepository = Depends(get_repository)):
    logger.info(f"Received registration request: {user.username}, {user.email}")
    user_auth_service = UserAuthService(repo)
    try:
        user_auth_service.register_user(user.username, user.email, user.password)
        logger.info(f"User registered successfully: {user.username}")
        return {"message": "User registered successfully"}
    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), repo: IUserRepository = Depends(get_repository)):
    logger.info(f"Login attempt received for user: {form_data.username}")
    user_auth_service = UserAuthService(repo)
    try:
        user = user_auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Invalid credentials for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        access_token = user_auth_service.generate_token(user)
        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
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
