import json
from typing import Optional, List
from models.user import User
from services.service_interfaces import IUserRepository
import os


class UserRepository(IUserRepository):
    def __init__(self, file_path: str = 'users.json'):
        self.file_path = file_path

    def _load_users(self):
        if not os.path.exists(self.file_path):
            return {}
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def _save_users(self, users):
        with open(self.file_path, 'w') as file:
            json.dump(users, file, indent=4)

    def get_by_id(self, user_id: int) -> Optional[User]:
        # Currently, we don't store user IDs in the JSON file
        # This method will always return None
        return None

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        users = self._load_users()
        # First, try to find by username
        user_data = users.get(identifier)
        if user_data:
            return User(
                user_id=None,
                user_name=identifier,
                email=user_data['email'],
                password_hash=user_data['password']
            )
        # If not found by username, try to find by email
        for username, data in users.items():
            if data['email'] == identifier:
                return User(
                    user_id=None,
                    user_name=username,
                    email=identifier,
                    password_hash=data['password']
                )
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        users = self._load_users()
        for username, user_data in users.items():
            if user_data['email'] == email:
                return User(
                    user_id=None,  # Note: There's no 'id' in the JSON, so we're using None
                    user_name=username,
                    email=email,
                    password_hash=user_data['password']
                )
        return None

    def get_all(self) -> List[User]:
        users = self._load_users()
        return [
            User(
                user_id=None,
                user_name=username,
                email=user_data['email'],
                password_hash=user_data['password']
            )
            for username, user_data in users.items()
        ]

    def create(self, user: User) -> User:
        users = self._load_users()
        if user.user_name in users:
            raise ValueError(f"User with username '{user.user_name}' already exists")
        users[user.user_name] = {
            'id': user.user_id,
            'email': user.email,
            'password': user.password_hash
        }
        self._save_users(users)
        return user

    def update(self, user: User) -> User:
        users = self._load_users()
        if user.user_name not in users:
            raise ValueError(f"User with username '{user.user_name}' not found")
        users[user.user_name] = {
            'id': user.user_id,
            'email': user.email,
            'password': user.password_hash
        }
        self._save_users(users)
        return user

    def delete(self, user: User) -> None:
        users = self._load_users()
        if user.user_name not in users:
            raise ValueError(f"User with username '{user.user_name}' not found")
        del users[user.user_name]
        self._save_users(users)