from abc import ABC, abstractmethod
from typing import List, Optional

from models.user import User


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