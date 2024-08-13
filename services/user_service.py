import uuid
from datetime import datetime

from models.user import User
from services.service_interfaces import IUserService, IUserRepository
from typing import Optional, List, Type


class UserService(IUserService):
    user_repository: IUserRepository

    def register_user(self, username: str, password: str) -> User:
        found_user = self.user_repository.get_by_user_name(username)
        if found_user is not None:
            raise Exception(f'user with username: {username} already exists')

        user = User(
            username=username,
        )
        user.set_password(password=password)
        self.user_repository.create(user)
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_user_name(username)
        if user and user.check_password(password):
            return user
        return None

    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        username, token_str = token.split("_")
        user = self.user_repository.get_by_user_name(username)
        if user is None:
            return None

        if not user.check_token(token):
            return None

        if (datetime.now() - user.token_issuance_date) > 90:
            return None

        return None

    def generate_token(self, user: User) -> str:
        token = str(uuid.uuid4())
        user.set_token(token)
        user.token_issuance_date = datetime.now()
        self.user_repository.update(user)
        return user.user_name + '_' + token
