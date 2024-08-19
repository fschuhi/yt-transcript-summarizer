"""
Main FastAPI application module for the YouTube Transcript Summarizer.

This module sets up the FastAPI application, configures CORS, logging, and defines
the API endpoints for user registration, authentication, and video summarization.
It uses various utility functions and services to handle database operations,
user authentication, and interaction with external APIs (YouTube and OpenAI).
"""

import logging
import os
import re
import sys
from functools import lru_cache
from typing import Optional

import colorama
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from repositories.repository_provider import get_repository
from services.service_interfaces import IUserRepository
from services.user_auth_service import UserAuthService
from utils import openai_utils

# do not change, used in test_summarize_endpoint_authorized for @patch
from utils.youtube_utils import get_youtube_data

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class SummarizeRequest(BaseModel):
    """
    Pydantic model for the summarize request payload.

    Attributes:
        video_url (str): The URL of the YouTube video to summarize.
        summary_length (int): The desired length of the summary in words.
        used_model (str): The OpenAI model to use for summarization.
    """
    video_url: str
    summary_length: int
    used_model: str


class UserCreate(BaseModel):
    """
    Pydantic model for user registration payload.

    Attributes:
        username (str): The desired username for the new user.
        email (str): The email address of the new user.
        password (str): The password for the new user account.
    """
    username: str
    email: str
    password: str


@lru_cache()
def get_secret_key() -> str:
    """
    Retrieve the secret key from environment variables.

    Returns:
        str: The secret key used for JWT token encoding/decoding.
    """
    return os.getenv("SECRET_KEY")


def get_current_user(
    token: str = Depends(oauth2_scheme), repo: IUserRepository = Depends(get_repository)
) -> str:
    """
    Dependency to get the current authenticated user.

    Args:
        token (str): The JWT token from the request.
        repo (IUserRepository): The user repository for database operations.

    Returns:
        str: The username of the authenticated user.

    Raises:
        HTTPException: If the credentials are invalid or expired.
    """
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
    """
    Extract the YouTube video ID from various URL formats or direct ID input.

    Args:
        input_string (str): The input string containing a YouTube URL or video ID.

    Returns:
        Optional[str]: The extracted video ID, or None if no valid ID is found.
    """
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)

    if re.match(r"^[a-zA-Z0-9_-]{11}$", input_string):
        return input_string

    return None


@app.get("/")
async def read_root(request: Request):
    """
    Forbid access to the root endpoint.

    This endpoint is no longer accessible due to changes in authentication method
    and overall API structure. It now returns a 403 Forbidden response.

    Args:
        request (Request): The incoming request object.

    Raises:
        HTTPException: Always raises a 403 Forbidden exception.
    """
    logger.info("Received request for root endpoint (forbidden)")
    raise HTTPException(status_code=403, detail="Access to this endpoint is forbidden")


@app.get("/health")
async def health_check():
    """
    Endpoint to check the health status of the API.

    Returns:
        dict: A dictionary containing the health status of the API.
    """
    logger.info("Health check endpoint hit")
    return {"status": "healthy"}


@app.post("/register")
async def register(user: UserCreate, repo: IUserRepository = Depends(get_repository)):
    """
    Endpoint for user registration.

    Args:
        user (UserCreate): The user registration data.
        repo (IUserRepository): The user repository for database operations.

    Returns:
        dict: A message indicating successful registration.

    Raises:
        HTTPException: If registration fails due to existing username/email or other errors.
    """
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
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    repo: IUserRepository = Depends(get_repository),
):
    """
    Endpoint for user login and token generation.

    Args:
        form_data (OAuth2PasswordRequestForm): The login credentials.
        repo (IUserRepository): The user repository for database operations.

    Returns:
        dict: A dictionary containing the access token and token type.

    Raises:
        HTTPException: If login fails due to invalid credentials or other errors.
    """
    logger.info(f"Login attempt received for user: {form_data.username}")
    user_auth_service = UserAuthService(repo)
    try:
        user = user_auth_service.authenticate_user(
            form_data.username, form_data.password
        )
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@app.post("/summarize")
async def summarize(
    summarize_request: SummarizeRequest, current_user: str = Depends(get_current_user)
):
    """
    Endpoint to summarize a YouTube video transcript.

    This function extracts the video ID from the provided URL, retrieves the transcript
    and metadata, and generates a summary using the specified OpenAI model.

    Args:
        summarize_request (SummarizeRequest): The request containing video URL and summarization parameters.
        current_user (str): The authenticated user making the request.

    Returns:
        dict: A dictionary containing the generated summary, word count, and video metadata.

    Raises:
        HTTPException: If there's an error in video ID extraction, transcript retrieval, or summarization.
    """
    logger.info(f"Received summarize request from user: {current_user}")

    try:
        video_id = extract_video_id(summarize_request.video_url)
        if not video_id:
            logger.error(f"Invalid YouTube URL: {summarize_request.video_url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        logger.info(f"Extracted video ID: {video_id}")
        youtube_data = get_youtube_data(video_id)

        if not youtube_data["transcript"]:
            logger.error(f"Failed to retrieve transcript for video ID: {video_id}")
            raise HTTPException(status_code=400, detail="Failed to retrieve transcript")

        full_text = " ".join(youtube_data["transcript"])
        logger.info(f"Transcript retrieved. Length: {len(full_text)} characters")

        summary = openai_utils.summarize_text(
            full_text,
            youtube_data["metadata"],
            summarize_request.summary_length,
            summarize_request.used_model,
        )
        logger.info(f"Summary generated. Length: {len(summary)} characters")

        word_count = len(summary.split())

        return {
            "summary": summary,
            "word_count": word_count,
            "metadata": youtube_data["metadata"],
        }
    except Exception as e:
        logger.exception(f"Error in summarize endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
