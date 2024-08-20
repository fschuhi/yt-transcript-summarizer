"""Tests for the main FastAPI application endpoints."""

import logging
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from services.dependencies import get_current_user, get_youtube_service, get_openai_service
from services.openai_api_service import OpenAIAPIService
from services.youtube_api_service import YouTubeAPIService
from .conftest import client, mock_openai_summary
from .test_utils import mocked_client_post

from main import app as main_app
app: FastAPI = main_app


logger = logging.getLogger(__name__)


def test_health_endpoint(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client: TestClient):
    """Test that the root endpoint returns a 403 Forbidden status."""
    response = client.get("/")
    assert response.status_code == 403
    assert response.json() == {"detail": "Access to this endpoint is forbidden"}


def test_register_endpoint(client: TestClient):
    """Test the user registration endpoint."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
    }

    mock_auth_service = MagicMock()
    mock_auth_service.register_user.return_value = None  # Simulate successful registration

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/register", json=user_data
    )

    assert response.status_code == 200
    assert response_json == {"message": "User registered successfully"}
    # Verify that register_user was called with correct arguments
    mock_auth_service.register_user.assert_called_once_with(
        user_data["username"], user_data["email"], user_data["password"]
    )


def test_token_endpoint_login_success(client: TestClient):
    """Test successful login and token generation."""
    login_data = {"username": "testuser", "password": "password123"}

    mock_auth_service = MagicMock()

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/token", data=login_data
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response_json["token_type"] == "bearer"
    # Verify authentication and token generation calls
    mock_auth_service.authenticate_user.assert_called_once_with(
        login_data["username"], login_data["password"]
    )
    mock_auth_service.generate_token.assert_called_once()


def test_token_endpoint_login_failure(client: TestClient):
    """Test login failure due to incorrect credentials."""
    login_data = {"username": "testuser", "password": "wrongpassword"}

    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user.return_value = None  # Simulate failed authentication

    response, response_json = mocked_client_post(
        client, mock_auth_service, "/token", data=login_data
    )

    assert response.status_code == 401
    assert response_json["detail"] == "Incorrect username or password"
    # Verify authentication attempt with incorrect credentials
    mock_auth_service.authenticate_user.assert_called_once_with(
        login_data["username"], login_data["password"]
    )


def override_dependency(app: FastAPI, dependency, override_func):
    """
    Regarding the PyCharm warnings about app.dependency_overrides, these occur because PyCharm's static analysis
    can't always correctly infer dynamic attributes of FastAPI applications.
    """
    # noinspection PyUnresolvedReferences
    app.dependency_overrides[dependency] = override_func


def test_summarize_endpoint_authorized(
        client: TestClient,
        mock_openai_summary: str,
        mock_youtube_data: Dict,
):
    # Setup mock YouTube service
    mock_youtube_service = MagicMock(spec=YouTubeAPIService)
    mock_youtube_service.get_youtube_transcript.return_value = mock_youtube_data['transcript']
    mock_youtube_service.get_video_metadata.return_value = mock_youtube_data['metadata']

    # Setup mock OpenAI service
    mock_openai_service = MagicMock(spec=OpenAIAPIService)
    mock_openai_service.summarize_text.return_value = mock_openai_summary

    # Mock the authentication
    mock_current_user = "testuser"

    # Override the dependencies
    override_dependency(app, get_youtube_service, lambda: mock_youtube_service)
    override_dependency(app, get_openai_service, lambda: mock_openai_service)
    override_dependency(app, get_current_user, lambda: mock_current_user)

    try:
        # Test data
        test_data = {
            "video_url": "https://www.youtube.com/watch?v=py5byOOHZM8",
            "summary_length": 300,
            "used_model": "gpt-4-mini",
        }

        # Create a dummy token for authentication (not actually used, but included for completeness)
        headers = {"Authorization": "Bearer dummy_token"}

        # Make the request to the /summarize endpoint
        response = client.post("/summarize", json=test_data, headers=headers)
        response_json = response.json()

        # Assertions
        assert response.status_code == 200, "Expected successful response"
        assert response_json["summary"] == mock_openai_summary, "Summary should match the mock data"
        assert response_json["word_count"] == len(
            mock_openai_summary.split()), "Word count should match the summary length"

        # Compare metadata excluding potentially changing fields
        assert {k: v for k, v in response_json["metadata"].items() if k not in ['view_count', 'like_count']} == \
               {k: v for k, v in mock_youtube_data["metadata"].items() if k not in ['view_count', 'like_count']}, \
            "Metadata should match the mock YouTube data (excluding view_count and like_count)"

        # Verify that our mock services were called correctly
        mock_youtube_service.get_youtube_transcript.assert_called_once_with("py5byOOHZM8", include_timestamps=False)
        mock_youtube_service.get_video_metadata.assert_called_once_with("py5byOOHZM8")
        mock_openai_service.summarize_text.assert_called_once()

    finally:
        # Clean up the dependency overrides
        # noinspection PyUnresolvedReferences
        app.dependency_overrides.clear()


def test_summarize_endpoint_unauthorized(client):
    """Test the summarize endpoint without proper authorization."""
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
