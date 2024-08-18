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
        users = self._load_users()
        for username, user_data in users.items():
            if user_data.get('id') == user_id:
                return User(
                    user_id=user_id,
                    user_name=username,
                    email=user_data['email'],
                    password_hash=user_data['password']
                )
        return None

    def get_by_user_name(self, user_name: str) -> Optional[User]:
        users = self._load_users()
        user_data = users.get(user_name)
        if user_data:
            return User(
                user_id=user_data.get('id'),
                user_name=user_name,
                email=user_data['email'],
                password_hash=user_data['password']
            )
        return None

    def get_all(self) -> List[User]:
        users = self._load_users()
        return [
            User(
                user_id=user_data.get('id'),
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