import json
import os
from typing import Dict, List, Optional

from models.user import User
from services.service_interfaces import IUserRepository


class UserJsonRepository(IUserRepository):
    def __init__(self, file_path: str = "users.json"):
        self.file_path = file_path

    def _load_users(self) -> Dict[str, Dict]:
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, "r") as file:
            return json.load(file)

    def _save_users(self, users: Dict[str, Dict]):
        with open(self.file_path, "w") as file:
            json.dump(users, file, indent=4)

    def get_by_id(self, user_id: int) -> Optional[User]:
        users = self._load_users()
        for user_data in users.values():
            if user_data["user_id"] == user_id:
                return User.from_dict(user_data)
        return None

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        users = self._load_users()
        user_data = users.get(identifier)
        if user_data:
            return User.from_dict(user_data)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        users = self._load_users()
        for user_data in users.values():
            if user_data["email"] == email:
                return User.from_dict(user_data)
        return None

    def get_all(self) -> List[User]:
        users = self._load_users()
        return [User.from_dict(user_data) for user_data in users.values()]

    def create(self, user: User) -> User:
        users = self._load_users()
        if user.user_name in users:
            raise ValueError(f"User with username '{user.user_name}' already exists")
        users[user.user_name] = user.to_dict()
        self._save_users(users)
        return user

    def update(self, user: User) -> User:
        users = self._load_users()
        if user.user_name not in users:
            raise ValueError(f"User with username '{user.user_name}' not found")
        users[user.user_name] = user.to_dict()
        self._save_users(users)
        return user

    def delete(self, user: User) -> None:
        users = self._load_users()
        if user.user_name not in users:
            raise ValueError(f"User with username '{user.user_name}' not found")
        del users[user.user_name]
        self._save_users(users)
