"""JSON-based implementation of the IUserRepository interface."""

import json
import os
from typing import Dict, List, Optional

from models.user import User
from services.service_interfaces import IUserRepository


class UserJsonRepository(IUserRepository):
    """Repository for managing User entities using JSON file storage."""

    def __init__(self, file_path: str = "users.json"):
        """Initialize the repository with the given JSON file path."""
        self.file_path = file_path

    def _load_users(self) -> Dict[str, Dict]:
        """Load users from the JSON file."""
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _save_users(self, users: Dict[str, Dict]):
        """Save users to the JSON file."""
        with open(self.file_path, "w") as file:
            json.dump(users, file, indent=4)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        users = self._load_users()
        for user_data in users.values():
            if user_data["user_id"] == user_id:
                return User.from_dict(user_data)
        return None

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username)."""
        users = self._load_users()
        user_data = users.get(identifier)
        if user_data:
            return User.from_dict(user_data)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        users = self._load_users()
        for user_data in users.values():
            if user_data["email"] == email:
                return User.from_dict(user_data)
        return None

    def get_all(self) -> List[User]:
        """Retrieve all users."""
        users = self._load_users()
        return [User.from_dict(user_data) for user_data in users.values()]

    def create(self, user: User) -> User:
        """Create a new user."""
        users = self._load_users()
        if user.user_name in users:
            raise ValueError(f"User with username '{user.user_name}' already exists")
        users[user.user_name] = user.to_dict()
        self._save_users(users)
        return user

    def update(self, user: User) -> User:
        """Update an existing user."""
        users = self._load_users()
        if user.user_name not in users:
            raise ValueError(f"User with username '{user.user_name}' not found")
        users[user.user_name] = user.to_dict()
        self._save_users(users)
        return user

    def delete(self, user: User) -> None:
        """Delete a user."""
        users = self._load_users()
        if user.user_name not in users:
            raise ValueError(f"User with username '{user.user_name}' not found")
        del users[user.user_name]
        self._save_users(users)
