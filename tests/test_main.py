import logging
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from .conftest import client, mock_openai_summary
from .test_utils import mocked_client_post

logger = logging.getLogger(__name__)


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client: TestClient):
    """
    Test that the root endpoint returns a 403 Forbidden status.
    """
    response = client.get("/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Access to this endpoint is forbidden"}


def test_register_endpoint(client: TestClient):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
    }

    mock_auth_service = MagicMock()
    mock_auth_service.register_user.return_value = (
        None  # Simulate successful registration
    )

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/register", json=user_data
    )

    assert response.status_code == 200
    assert response_json == {"message": "User registered successfully"}
    mock_auth_service.register_user.assert_called_once_with(
        user_data["username"], user_data["email"], user_data["password"]
    )


def test_token_endpoint_login_success(client: TestClient):
    login_data = {"username": "testuser", "password": "password123"}

    mock_auth_service = MagicMock()

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/token", data=login_data
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response_json["token_type"] == "bearer"
    mock_auth_service.authenticate_user.assert_called_once_with(
        login_data["username"], login_data["password"]
    )
    mock_auth_service.generate_token.assert_called_once()


def test_token_endpoint_login_failure(client: TestClient):
    login_data = {"username": "testuser", "password": "wrongpassword"}

    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user.return_value = (
        None  # Simulate failed authentication
    )

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/token", data=login_data
    )

    assert response.status_code == 401
    assert response_json["detail"] == "Incorrect username or password"
    mock_auth_service.authenticate_user.assert_called_once_with(
        login_data["username"], login_data["password"]
    )


@patch("main.get_youtube_data")
@patch("main.openai_utils.summarize_text")
def test_summarize_endpoint_authorized(
    mock_summarize_text: MagicMock,
    mock_get_youtube_data: MagicMock,
    client: TestClient,
    mock_openai_summary: str,
    mock_youtube_data: Dict,
):
    # Setup mock data
    mock_get_youtube_data.return_value = mock_youtube_data
    mock_summarize_text.return_value = mock_openai_summary

    # Test data
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=py5byOOHZM8",
        "summary_length": 300,
        "used_model": "gpt-4-mini",
    }

    # Create a dummy token (the actual value doesn't matter as we're mocking the validation)
    dummy_token = "dummy_token"

    # Make request
    headers = {"Authorization": f"Bearer {dummy_token}"}

    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user_by_token.return_value = MagicMock(
        user_name="testuser"
    )

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/summarize", json=test_data, headers=headers
    )

    assert response.status_code == 200

    # Assert response
    assert "summary" in response_json
    assert response_json["summary"] == mock_openai_summary
    assert "word_count" in response_json
    assert response_json["word_count"] == len(mock_openai_summary.split())
    assert "metadata" in response_json
    assert response_json["metadata"] == mock_youtube_data["metadata"]

    # Verify mock calls
    mock_get_youtube_data.assert_called_once_with("py5byOOHZM8")
    mock_summarize_text.assert_called_once_with(
        " ".join(mock_youtube_data["transcript"]),
        mock_youtube_data["metadata"],
        300,
        "gpt-4-mini",
    )


def test_summarize_endpoint_unauthorized(client):
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=py5byOOHZM8",
        "summary_length": 300,
        "used_model": "gpt-4-mini",
    }
    response = client.post("/summarize", json=test_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


if __name__ == "__main__":
    pytest.main()
