import os
# noinspection PyUnresolvedReferences
import pytest
from unittest.mock import patch, MagicMock
from .conftest import mock_openai_summary, client
# noinspection PyPackageRequirements
from repositories.user_json_repository import UserJsonRepository
from repositories.user_db_repository import UserDBRepository
import logging

from .test_utils import mock_repo_and_auth_service, mock_auth_and_get_token

logger = logging.getLogger(__name__)


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

    mock_repo, mock_auth_service = mock_repo_and_auth_service()
    mock_auth_service.register_user.return_value = None  # Simulate successful registration

    # Patch the get_repository function to return our mock repository
    with patch('main.get_repository', return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/register", json=user_data)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    assert response.status_code == 200
    assert response.json() == {"message": "User registered successfully"}
    mock_auth_service.register_user.assert_called_once_with(
        user_data["username"], user_data["email"], user_data["password"]
    )


def test_login_success(client):
    login_data = {
        "username": "testuser",
        "password": "password123"
    }

    mock_repo, mock_auth_service = mock_repo_and_auth_service()
    token = mock_auth_and_get_token(mock_auth_service)

    with patch('main.get_repository', return_value=mock_repo):
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/token", data=login_data)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

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

    mock_repo, mock_auth_service = mock_repo_and_auth_service()
    mock_auth_service.authenticate_user.return_value = None  # Simulate failed authentication

    with patch('main.get_repository', return_value=mock_repo):
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post("/token", data=login_data)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
    mock_auth_service.authenticate_user.assert_called_once_with(login_data["username"], login_data["password"])


@patch('main.get_youtube_data')
@patch('main.openai_utils.summarize_text')
def test_summarize_endpoint(mock_summarize_text, mock_get_youtube_data, client, mock_openai_summary, mock_youtube_data):
    # Setup mock data
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

    mock_repo, mock_auth_service = mock_repo_and_auth_service()
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
