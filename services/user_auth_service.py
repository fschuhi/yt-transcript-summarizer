import uuid
from datetime import datetime, timedelta

from models.user import User
from services.service_interfaces import IUserAuthService, IUserRepository
from typing import Optional


class UserAuthService(IUserAuthService):
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    def register_user(self, username: str, email: str, password: str) -> User:
        found_user = self.user_repository.get_by_identifier(username)
        if found_user is not None:
            raise Exception(f'User with username: {username} already exists')

        if self.user_repository.get_by_email(email):
            raise Exception(f'User with email: {email} already exists')

        user = User(
            user_id=None,
            user_name=username,
            email=email,
            password_hash=''
        )
        user.set_password(password)
        return self.user_repository.create(user)

    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_identifier(identifier)
        if user and user.check_password(password):
            return user
        return None

    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        username, token_str = token.split("_")
        user = self.user_repository.get_by_identifier(username)
        if user is None:
            return None

        if not user.check_token(token):
            return None

        if (datetime.now() - user.token_issuance_date) > timedelta(days=90):
            return None

        return user

    def generate_token(self, user: User) -> str:
        token = str(uuid.uuid4())
        user.set_token(token)
        user.token_issuance_date = datetime.now()
        self.user_repository.update(user)
        return f"{user.user_name}_{token}"

    def get_user(self, identifier: str) -> Optional[User]:
        return self.user_repository.get_by_identifier(identifier)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repository.get_by_email(email)

    def update_user_email(self, user: User, new_email: str) -> User:
        user.email = new_email
        return self.user_repository.update(user)
