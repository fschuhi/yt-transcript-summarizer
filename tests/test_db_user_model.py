"""Tests for the database User model and UserDBRepository."""

from datetime import datetime

import pytest

import utils.db_test_utils as db_utils
from models.user import User
from repositories.user_db_repository import UserDBRepository
from utils.auth_utils import AuthenticationUtils


def test_user_set_password():
    """Test the password hashing and verification for a User."""
    password = "hashed_password"
    user = User(
        user_id=None, user_name="testuser", email="test@example.com", password_hash=""
    )
    user.password_hash = AuthenticationUtils.hash_password(password)
    assert AuthenticationUtils.verify_password(password, user.password_hash)


def create_default_user(password: str, token: str) -> User:
    """Create a default user for testing purposes.

    Returns: A User instance with predefined attributes.
    """
    user = User(
        user_id=None,
        user_name="summaria@summaria.com",
        email="summaria@summaria.com",
        password_hash=AuthenticationUtils.hash_password(password),
    )
    user.token = AuthenticationUtils.hash_password(token)
    user.last_login_date = datetime(2023, 5, 1, 10, 30, 0)
    user.token_issuance_date = datetime(2023, 5, 1, 10, 30, 0)
    user.identity_provider = "local"
    return user


@pytest.mark.db
def test_user_model(setup_database):
    """Test creating, retrieving, and deleting a user in the database."""
    db_session = db_utils.create_db_session()
    password = "hashed_password"
    token = "test_token"
    user = create_default_user(password=password, token=token)
    user_repository = UserDBRepository(db_session)

    # Create user
    user_repository.create(user)

    # Retrieve user
    reloaded_user = user_repository.get_by_identifier(identifier=user.user_name)

    # Verify user attributes
    assert isinstance(reloaded_user, User)
    assert reloaded_user.user_name == user.user_name
    assert reloaded_user.email == user.email
    assert reloaded_user.last_login_date == user.last_login_date
    assert reloaded_user.token_issuance_date == user.token_issuance_date
    assert AuthenticationUtils.verify_password(token, reloaded_user.token)
    assert AuthenticationUtils.verify_password(password, reloaded_user.password_hash)
    assert reloaded_user.identity_provider == user.identity_provider

    # Delete user
    user_repository.delete(reloaded_user)


@pytest.mark.db
def test_user_repository_get_by_user_name(setup_database):
    """Test retrieving a user by username using UserDBRepository."""
    db_session = db_utils.create_db_session()
    password = "hashed_password"
    token = "test_token"
    user = create_default_user(password=password, token=token)
    user_repository = UserDBRepository(db_session)

    # Create user
    user_repository.create(user)

    # Retrieve user by username
    reloaded_user = user_repository.get_by_identifier(identifier=user.user_name)
    assert isinstance(reloaded_user, User)
    assert reloaded_user.user_name == user.user_name
