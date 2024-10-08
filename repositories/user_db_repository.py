"""Database-based implementation of the IUserRepository interface."""

from typing import List, Optional, cast

from sqlalchemy.orm import Session

from models.user import User
from .repository_interfaces import IUserRepository


class UserDBRepository(IUserRepository):
    """Repository for managing User entities using a database."""

    def __init__(self, session: Session):
        """Initialize the repository with a database session."""
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username)."""
        return self.session.query(User).filter_by(user_name=identifier).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        return self.session.query(User).filter_by(email=email).first()

    def get_all(self) -> List[User]:
        """Retrieve all users."""
        return cast(List[User], self.session.query(User).all())

    def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user: User) -> User:
        """Update an existing user."""
        self.session.merge(user)
        self.session.commit()
        return user

    def delete(self, user: User) -> None:
        """Delete a user."""
        self.session.delete(user)
        self.session.commit()
