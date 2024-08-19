"""Implementation of user authentication and management services."""

from typing import Optional

from models.user import User
from services.service_interfaces import IUserAuthService, IUserRepository
from utils.auth_utils import DEFAULT_SECRET_KEY, AuthenticationUtils


class UserAlreadyExistsError(ValueError):
    """Raised when attempting to register a user with an existing username or email."""
    pass


class UserAuthService(IUserAuthService):
    """Concrete implementation of the IUserAuthService interface."""

    def __init__(
        self, user_repository: IUserRepository, secret_key: str = DEFAULT_SECRET_KEY
    ):
        """Initialize the UserAuthService.

        Args:
            user_repository: Repository for user data operations.
            secret_key: Secret key for JWT token generation and verification.
        """
        self.user_repository = user_repository
        self.secret_key = secret_key

    def register_user(self, username: str, email: str, password: str) -> User:
        """Register a new user after checking for existing username and email.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password (will be hashed).
        Returns: The created User object.
        Raises: UserAlreadyExistsError if username or email is already in use.
        """
        if self.user_repository.get_by_identifier(username):
            raise UserAlreadyExistsError(f"User with username '{username}' already exists")

        if self.user_repository.get_by_email(email):
            raise UserAlreadyExistsError(f"User with email '{email}' already exists")

        hashed_password = AuthenticationUtils.hash_password(password)
        user = User(user_id=None, user_name=username, email=email, password_hash=hashed_password)
        return self.user_repository.create(user)

    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Authenticate a user by identifier (username or email) and password.

        Args:
            identifier: The username or email of the user.
            password: The password to verify.
        Returns: The authenticated User object if successful, None otherwise.
        """
        user = self.user_repository.get_by_identifier(identifier)
        if user and AuthenticationUtils.verify_password(password, user.password_hash):
            return user
        return None

    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        """Authenticate a user using a JWT token.

        Args:
            token: The JWT token to verify.
        Returns: The authenticated User object if successful, None otherwise.
        """
        username = AuthenticationUtils.verify_jwt_token(token, secret_key=self.secret_key)
        return self.user_repository.get_by_identifier(username) if username else None

    def generate_token(self, user: User) -> str:
        """Generate a JWT token for the given user."""
        return AuthenticationUtils.generate_jwt_token(user.user_name, secret_key=self.secret_key)

    def get_user(self, identifier: str) -> Optional[User]:
        """Retrieve a user by their identifier (username or email)."""
        return self.user_repository.get_by_identifier(identifier)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        return self.user_repository.get_by_email(email)

    def update_user_email(self, user: User, new_email: str) -> User:
        """Update a user's email address.

        Args:
            user: The User object to update.
            new_email: The new email address.
        Returns: The updated User object.
        Raises: ValueError if the new email is already in use by another user.
        """
        existing_email_user = self.user_repository.get_by_email(new_email)
        if existing_email_user and existing_email_user.user_id != user.user_id:
            raise ValueError(f"Email '{new_email}' is already in use")

        user.email = new_email
        return self.user_repository.update(user)
