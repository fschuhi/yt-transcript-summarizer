import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from .test_helpers import get_mock_youtube_data, mock_openai_summary, mock_env_variables
from .test_helpers import mock_token_provider
# noinspection PyUnresolvedReferences
from .test_helpers import mock_api_key_provider
# noinspection PyPackageRequirements
from jose import jwt
from repositories.user_json_repository import UserJsonRepository
from repositories.user_db_repository import UserDBRepository
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def client(mock_env_variables, mock_token_provider):
    """
    Fixture to create a test client for the FastAPI application with mocked JWT token validation.

    This fixture does the following:
    1. Uses the mock_env_variables fixture to set up mock environment variables.
    2. Uses the mock_token_provider to get a consistent dummy JWT token.
    3. Patches the get_current_user function to return a dummy username.
    4. Creates and yields a TestClient instance for the FastAPI app.

    :param mock_env_variables: Fixture that sets up mock environment variables.
    :param mock_token_provider: Fixture that provides a MockTokenProvider instance.
    :return: A TestClient instance for the FastAPI application.
    """
    dummy_username = "testuser"

    with patch('main.get_current_user', return_value=dummy_username):
        with TestClient(app) as test_client:
            logger.info("TestClient created with mocked current user")
            yield test_client


def test_repository_type(client):
    repository_type = os.getenv("USER_REPOSITORY_TYPE", "json")

    # Create an instance of the appropriate repository type
    if repository_type == "postgres":
        expected_repo = UserDBRepository(MagicMock())  # Pass a mock Session
    else:
        expected_repo = UserJsonRepository('test_users.json')

    with patch('main.get_repository', return_value=expected_repo):
        response = client.get("/health")
        assert response.status_code == 200

    # Verify the type of repository used
    if repository_type == "postgres":
        assert isinstance(expected_repo, UserDBRepository), f"Expected UserDBRepository, got {type(expected_repo)}"
    else:
        assert isinstance(expected_repo, UserJsonRepository), f"Expected UserJsonRepository, got {type(expected_repo)}"

    logger.info(f"Confirmed repository type: {type(expected_repo).__name__}")


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    """
    Test that the root endpoint returns a 403 Forbidden status.
    """
    response = client.get("/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Access to this endpoint is forbidden"}


def test_register(client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }

    # Create a mock repository
    mock_repo = MagicMock()

    # Create a mock UserAuthService
    mock_auth_service = MagicMock()
    mock_auth_service.register_user.return_value = None  # Simulate successful registration

    # Patch the get_repository function to return our mock repository
    with patch('main.get_repository', return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/register", json=user_data)

    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}

    # Assert that register_user was called on our mock auth service
    mock_auth_service.register_user.assert_called_once_with(
        user_data["username"], user_data["email"], user_data["password"]
    )


def test_login_success(client):
    login_data = {
        "username": "testuser",
        "password": "password123"
    }

    # Create a mock repository
    mock_repo = MagicMock()

    # Create a mock UserAuthService
    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user.return_value = MagicMock()  # Simulate successful authentication
    mock_auth_service.generate_token.return_value = "dummy_token"

    # Patch the get_repository function to return our mock repository
    with patch('main.get_repository', return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/token", data=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    mock_auth_service.authenticate_user.assert_called_once_with(login_data["username"], login_data["password"])
    mock_auth_service.generate_token.assert_called_once()


def test_login_failure(client):
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }

    # Create a mock repository
    mock_repo = MagicMock()

    # Create a mock UserAuthService
    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user.return_value = None  # Simulate failed authentication

    # Patch the get_repository function to return our mock repository
    with patch('main.get_repository', return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/token", data=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    mock_auth_service.authenticate_user.assert_called_once_with(login_data["username"], login_data["password"])


@patch('main.get_youtube_data')
@patch('main.openai_utils.summarize_text')
def test_summarize_endpoint(mock_summarize_text, mock_get_youtube_data, client, mock_openai_summary):
    # Setup mock data
    mock_youtube_data = get_mock_youtube_data()
    mock_get_youtube_data.return_value = mock_youtube_data
    mock_summarize_text.return_value = mock_openai_summary

    # Test data
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=py5byOOHZM8",
        "summary_length": 300,
        "used_model": "gpt-4-mini"
    }

    # Create a dummy token (the actual value doesn't matter as we're mocking the validation)
    dummy_token = "dummy_token"

    # Make request
    headers = {"Authorization": f"Bearer {dummy_token}"}

    # Create a mock repository
    mock_repo = MagicMock()

    # Create a mock UserAuthService
    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user_by_token.return_value = MagicMock(user_name='testuser')

    # Patch the get_repository function to return our mock repository
    with patch('main.get_repository', return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/summarize", json=test_data, headers=headers)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    assert response.status_code == 200

    # Assert response
    response_data = response.json()
    assert "summary" in response_data
    assert response_data["summary"] == mock_openai_summary
    assert "word_count" in response_data
    assert response_data["word_count"] == len(mock_openai_summary.split())
    assert "metadata" in response_data
    assert response_data["metadata"] == mock_youtube_data["metadata"]

    # Verify mock calls
    mock_get_youtube_data.assert_called_once_with("py5byOOHZM8")
    mock_summarize_text.assert_called_once_with(
        ' '.join(mock_youtube_data['transcript']),
        mock_youtube_data['metadata'],
        300,
        "gpt-4-mini"
    )


def test_summarize_unauthorized(client):
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=py5byOOHZM8",
        "summary_length": 300,
        "used_model": "gpt-4-mini"
    }
    response = client.post("/summarize", json=test_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


if __name__ == "__main__":
    pytest.main()
