from typing import Optional

from models.user import User
from services.service_interfaces import IUserAuthService, IUserRepository
from utils.auth_utils import DEFAULT_SECRET_KEY, AuthenticationUtils


class UserAlreadyExistsError(ValueError):
    """Raised when attempting to register a user with an existing username or email."""

    pass


class UserAuthService(IUserAuthService):
    def __init__(
        self, user_repository: IUserRepository, secret_key: str = DEFAULT_SECRET_KEY
    ):
        self.user_repository = user_repository
        self.secret_key = secret_key

    def register_user(self, username: str, email: str, password: str) -> User:
        existing_user = self.user_repository.get_by_identifier(username)
        if existing_user:
            raise UserAlreadyExistsError(
                f"User with username '{username}' already exists"
            )

        existing_email = self.user_repository.get_by_email(email)
        if existing_email:
            raise UserAlreadyExistsError(f"User with email '{email}' already exists")

        hashed_password = AuthenticationUtils.hash_password(password)
        user = User(
            user_id=None, user_name=username, email=email, password_hash=hashed_password
        )
        return self.user_repository.create(user)

    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_identifier(identifier)
        if user and AuthenticationUtils.verify_password(password, user.password_hash):
            return user
        return None

    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        username = AuthenticationUtils.verify_jwt_token(
            token, secret_key=self.secret_key
        )
        if username:
            return self.user_repository.get_by_identifier(username)
        return None

    def generate_token(self, user: User) -> str:
        return AuthenticationUtils.generate_jwt_token(
            user.user_name, secret_key=self.secret_key
        )

    def get_user(self, identifier: str) -> Optional[User]:
        return self.user_repository.get_by_identifier(identifier)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repository.get_by_email(email)

    def update_user_email(self, user: User, new_email: str) -> User:
        existing_email = self.user_repository.get_by_email(new_email)
        if existing_email and existing_email.user_id != user.user_id:
            raise ValueError(f"Email '{new_email}' is already in use")

        user.email = new_email
        return self.user_repository.update(user)
