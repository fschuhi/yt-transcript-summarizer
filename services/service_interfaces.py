"""Interfaces for user authentication services and user repository operations."""

from abc import ABC, abstractmethod
from typing import List, Optional

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


class IUserRepository(ABC):
    """Interface for user data storage and retrieval operations."""

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        pass

    @abstractmethod
    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username or email)."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        """Retrieve all users."""
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user record."""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user record."""
        pass

    @abstractmethod
    def delete(self, user: User) -> None:
        """Delete a user record."""
        pass