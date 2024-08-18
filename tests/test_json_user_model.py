import pytest
import os
from models.user import User
from repositories.user_json_repository import UserJsonRepository
from services.user_auth_service import UserAuthService, UserAlreadyExistsError
from utils.auth_utils import AuthenticationUtils


@pytest.fixture
def user_repository():
    test_file = 'test_users.json'
    repo = UserJsonRepository(test_file)
    yield repo
    # Clean up after test
    if os.path.exists(test_file):
        os.remove(test_file)


@pytest.fixture
def user_auth_service(user_repository):
    return UserAuthService(user_repository)


def test_create_user(user_repository):
    user = User(user_id=None, user_name="testuser", email="test@example.com", password_hash="hashed_password")
    created_user = user_repository.create(user)
    assert created_user.user_name == "testuser"
    assert created_user.email == "test@example.com"


def test_get_user_by_identifier(user_repository):
    user = User(user_id=None, user_name="testuser", email="test@example.com", password_hash="hashed_password")
    user_repository.create(user)
    retrieved_user = user_repository.get_by_identifier("testuser")
    assert retrieved_user is not None
    assert retrieved_user.user_name == "testuser"
    assert retrieved_user.email == "test@example.com"


def test_get_user_by_email(user_repository):
    user = User(user_id=None, user_name="testuser", email="test@example.com", password_hash="hashed_password")
    user_repository.create(user)
    retrieved_user = user_repository.get_by_email("test@example.com")
    assert retrieved_user is not None
    assert retrieved_user.user_name == "testuser"
    assert retrieved_user.email == "test@example.com"


def test_update_user(user_repository):
    user = User(user_id=None, user_name="testuser", email="test@example.com", password_hash="hashed_password")
    created_user = user_repository.create(user)
    created_user.email = "newemail@example.com"
    updated_user = user_repository.update(created_user)
    assert updated_user.email == "newemail@example.com"


def test_delete_user(user_repository):
    user = User(user_id=None, user_name="testuser", email="test@example.com", password_hash="hashed_password")
    user_repository.create(user)
    user_repository.delete(user)
    assert user_repository.get_by_identifier("testuser") is None


def test_register_user(user_auth_service):
    user = user_auth_service.register_user("testuser", "test@example.com", "password123")
    assert user.user_name == "testuser"
    assert user.email == "test@example.com"
    assert AuthenticationUtils.verify_password("password123", user.password_hash)


def test_register_duplicate_user(user_auth_service):
    user_auth_service.register_user("testuser", "test@example.com", "password123")
    with pytest.raises(UserAlreadyExistsError):
        user_auth_service.register_user("testuser", "another@example.com", "password456")


def test_authenticate_user(user_auth_service):
    user_auth_service.register_user("testuser", "test@example.com", "password123")
    authenticated_user = user_auth_service.authenticate_user("testuser", "password123")
    assert authenticated_user is not None
    assert authenticated_user.user_name == "testuser"

    # Test with wrong password
    assert user_auth_service.authenticate_user("testuser", "wrongpassword") is None


def test_generate_and_authenticate_token(user_auth_service):
    user = user_auth_service.register_user("testuser", "test@example.com", "password123")
    token = user_auth_service.generate_token(user)
    authenticated_user = user_auth_service.authenticate_user_by_token(token)
    assert authenticated_user is not None
    assert authenticated_user.user_name == "testuser"

    # Test with invalid token
    assert user_auth_service.authenticate_user_by_token("invalid_token") is None
