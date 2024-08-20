"""Interfaces for user authentication services and user repository operations."""

from abc import ABC, abstractmethod
from typing import Optional

from models.user import User


class IUserAuthService(ABC):
    """Interface for user authentication and management operations."""

    @abstractmethod
    def register_user(self, username: str, email: str, password: str) -> User:
        """Register a new user."""
        pass

    @abstractmethod
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by identifier (username or email) and password."""
        pass

    @abstractmethod
    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        """Authenticate a user using a token."""
        pass

    @abstractmethod
    def generate_token(self, user: User) -> str:
        """Generate an authentication token for a user."""
        pass

    @abstractmethod
    def get_user(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username or email)."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        pass

    @abstractmethod
    def update_user_email(self, user: User, new_email: str) -> User:
        """Update a user's email address."""
        pass


"""Interfaces for user authentication services and user repository operations."""

from abc import ABC, abstractmethod
from typing import Optional

from models.user import User


class IUserAuthService(ABC):
    """Interface for user authentication and management operations."""

    @abstractmethod
    def register_user(self, username: str, email: str, password: str) -> User:
        """Register a new user."""
        pass

    @abstractmethod
    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by identifier (username or email) and password."""
        pass

    @abstractmethod
    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        """Authenticate a user using a token."""
        pass

    @abstractmethod
    def generate_token(self, user: User) -> str:
        """Generate an authentication token for a user."""
        pass

    @abstractmethod
    def get_user(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username or email)."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        pass

    @abstractmethod
    def update_user_email(self, user: User, new_email: str) -> User:
        """Update a user's email address."""
        pass


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
        pass