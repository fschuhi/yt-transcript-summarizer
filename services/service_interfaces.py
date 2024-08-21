"""Interfaces for user authentication, OpenAI, and YouTube API services.

This module defines abstract base classes that serve as contracts for various services
used in the application. These interfaces ensure consistency across different implementations
and facilitate easier testing and dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Union, List

from models.user import User


class IUserAuthService(ABC):
    """Interface for user authentication and management operations."""

    @abstractmethod
    def register_user(self, username: str, email: str, password: str) -> User:
        """Register a new user."""

    @abstractmethod
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by identifier (username or email) and password."""

    @abstractmethod
    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        """Authenticate a user using a token."""

    @abstractmethod
    def generate_token(self, user: User) -> str:
        """Generate an authentication token for a user."""

    @abstractmethod
    def get_user(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username or email)."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""

    @abstractmethod
    def update_user_email(self, user: User, new_email: str) -> User:
        """Update a user's email address."""


class IOpenAIAPIService(ABC):
    """Interface for OpenAI service operations."""

    @abstractmethod
    def summarize_text(self, text: str, metadata: dict, max_words: int, used_model: str = "gpt-3.5-turbo") -> str:
        """Summarize given text using OpenAI's API, incorporating video metadata.

        Args:
            text: The transcript text to summarize.
            metadata: Dict containing video metadata (title, channel, etc.).
            max_words: Target word count for the summary.
            used_model: OpenAI model to use (default: gpt-3.5-turbo).
        Returns: Summarized text or empty string if an error occurs.
        """


class IYouTubeAPIService(ABC):
    """Interface for YouTube Data API service operations."""

    @abstractmethod
    def get_youtube_transcript(
            self, video_id: str, include_timestamps: bool = True
    ) -> Union[List[Dict[str, Union[str, float]]], List[str]]:
        """Retrieve the transcript for a YouTube video.

        Args:
            video_id: The YouTube video ID.
            include_timestamps: Whether to include timestamps in the output.
        Returns: List of transcript segments, with or without timestamps.
        """

    @abstractmethod
    def get_video_metadata(self, video_id: str) -> Dict[str, Union[str, int]]:
        """Retrieve metadata for a YouTube video using the YouTube Data API.

        Args:
            video_id: The YouTube video ID.
        Returns: Dictionary containing video metadata.
        """
