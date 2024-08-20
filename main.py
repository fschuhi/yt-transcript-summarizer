"""Main FastAPI application module for the YouTube Transcript Summarizer.

Sets up the FastAPI app, configures CORS, logging, and defines API endpoints for
user registration, authentication, and video summarization. Uses utility functions
and services for database operations, user auth, and external API interactions.
"""

import argparse
import logging
import sys

import colorama
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn

from models.api_models import SummarizeRequest, UserCreate
from services.user_auth_service import UserAuthService
from services.dependencies import get_user_auth_service2, get_current_user
from utils import openai_utils
from utils import youtube_utils

# do not change, used in test_summarize_endpoint_authorized for @patch
#from utils.youtube_utils import get_youtube_data, extract_video_id

colorama.init()
load_dotenv()

# CORS middleware setup
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://vue.fschuhi.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root_endpoint():
    """Forbid access to the root endpoint."""
    logger.info("Received request for root endpoint (forbidden)")
    raise HTTPException(status_code=403, detail="Access to this endpoint is forbidden")


@app.get("/health")
async def health_endpoint():
    """Endpoint to check the health status of the API."""
    logger.info("Health check endpoint hit")
    return {"status": "healthy"}


@app.post("/register")
async def register_endpoint(
    user: UserCreate,
    user_auth_service: UserAuthService = Depends(get_user_auth_service2)
):
    """Endpoint for user registration.

    Args:
        user: The user registration data.
        user_auth_service: injected service which does authentication
    Returns: A message indicating successful registration.
    Raises: HTTPException: If registration fails due to existing username/email or other errors.
    """
    logger.info(f"Received registration request: {user.username}, {user.email}")
    try:
        user_auth_service.register_user(user.username, user.email, user.password)
        logger.info(f"User registered successfully: {user.username}")
        return {"message": "User registered successfully"}
    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/token")
async def token_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_auth_service: UserAuthService = Depends(get_user_auth_service2)
):
    """Endpoint for user login and token generation.

    Args:
        form_data: The login credentials.
        user_auth_service: injected service which does authentication
    Returns: A dictionary containing the access token and token type.
    Raises: HTTPException: If login fails due to invalid credentials or other errors.
    """
    logger.info(f"Login attempt received for user: {form_data.username}")
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
async def summarize_endpoint(
    summarize_request: SummarizeRequest,
    current_user: str = Depends(get_current_user)
):
    """Endpoint to summarize a YouTube video transcript.

    Args:
        summarize_request: The request containing video URL and summarization parameters.
        current_user: The authenticated user making the request.
    Returns: A dictionary containing the generated summary, word count, and video metadata.
    Raises: HTTPException: If there's an error in video ID extraction, transcript retrieval, or summarization.
    """
    logger.info(f"Received summarize request from user: {current_user}")

    try:
        video_id = youtube_utils.extract_video_id(summarize_request.video_url)
        if not video_id:
            logger.error(f"Invalid YouTube URL: {summarize_request.video_url}")
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        logger.info(f"Extracted video ID: {video_id}")
        youtube_data = youtube_utils.get_youtube_data(video_id)

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
    parser = argparse.ArgumentParser(description="Run the FastAPI application")
    parser.add_argument("--no-reload", action="store_false", dest="reload", help="Disable auto-reload")
    args = parser.parse_args()

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=args.reload)
