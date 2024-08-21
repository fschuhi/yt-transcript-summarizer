"""Dependency injection module for FastAPI application.

This module defines and provides dependencies for various services used in the application,
including user authentication, YouTube API, and OpenAI API services.
"""

from fastapi import Depends, HTTPException
from starlette import status
from fastapi.security import OAuth2PasswordBearer
from youtube_transcript_api import YouTubeTranscriptApi
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from openai import OpenAI

from services.user_auth_service import UserAuthService
from services.service_interfaces import IUserAuthService
from repositories.repository_provider import get_repository, IUserRepository
from services.youtube_api_service import YouTubeAPIService
from services.openai_api_service import OpenAIAPIService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_auth_service2(repo: IUserRepository = Depends(get_repository)) -> IUserAuthService:
    """Provide an instance of UserAuthService.

    Args:
        repo: An instance of IUserRepository, injected by FastAPI.

    Returns: An instance of IUserAuthService (specifically, UserAuthService).
    """
    return UserAuthService(repo)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: IUserAuthService = Depends(get_user_auth_service2)
) -> str:
    """Dependency to get the current authenticated user.

    Args:
        token: The JWT token from the request, injected by FastAPI.
        auth_service: An instance of IUserAuthService, injected by FastAPI.

    Returns: The username of the authenticated user.

    Raises: HTTPException: If the credentials cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = auth_service.authenticate_user_by_token(token)
        if user is None:
            raise credentials_exception
        return user.user_name
    except Exception:
        raise credentials_exception


def get_youtube_service() -> YouTubeAPIService:
    """Provide an instance of YouTubeAPIService.

    Returns: An instance of YouTubeAPIService with YouTubeTranscriptApi and build function injected.
    """
    return YouTubeAPIService(
        youtube_transcript_api=YouTubeTranscriptApi,
        youtube_build=build
    )


def get_openai_service() -> OpenAIAPIService:
    """Provide an instance of OpenAIAPIService.

    Returns: An instance of OpenAIAPIService with OpenAI client injected.
    """
    return OpenAIAPIService(client=OpenAI())
