"""Tests for the main FastAPI application endpoints."""

import logging
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from .conftest import client, mock_openai_summary
from .test_utils import mocked_client_post

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


@patch("main.get_youtube_data")
@patch("main.openai_utils.summarize_text")
def test_summarize_endpoint_authorized(
        mock_summarize_text: MagicMock,
        mock_get_youtube_data: MagicMock,
        client: TestClient,
        mock_openai_summary: str,
        mock_youtube_data: Dict,
):
    """Test the summarize endpoint with valid authorization.

    This test simulates the entire process of summarizing a YouTube video,
    including authentication, YouTube data retrieval, and text summarization.
    It uses extensive mocking to avoid actual API calls and database operations.

    The test covers:
    1. Authorization process
    2. YouTube data retrieval
    3. Text summarization
    4. Response structure and content verification

    Patching explanation:
    - We use @patch("main.get_youtube_data") because get_youtube_data is imported
      directly in the main module.
    - We use @patch("main.openai_utils.summarize_text") because summarize_text
      is imported from openai_utils in the main module.

    This difference in patching paths reflects how these functions are imported
    and used within the main module. It's crucial to patch the objects where they
    are looked up, not where they are defined.

    We avoid using @patch.object here because:
    1. @patch.object is typically used when you have direct access to the object
       you're patching, which isn't the case in a separate test module.
    2. @patch is more flexible when dealing with imports and module-level functions.
    3. @patch correctly handles the dynamic nature of Python's import system,
       ensuring we're mocking the correct objects as seen by the code under test.

    The ordering of patches is important: the innermost decorator corresponds
    to the leftmost argument in the test function.

    Under the hood:
    1. These patches replace the real functions with MagicMock objects.
    2. The MagicMock objects are passed as arguments to our test function.
    3. We configure these mocks to return our predefined test data.
    4. When the endpoint code runs, it calls these mocked functions instead of the real ones.
    5. After the test, the patches are automatically removed, restoring the original functions.

    This approach allows us to test the endpoint's logic without making actual API calls,
    providing a controlled environment for our test scenarios.
    """
    # Setup mock data
    mock_get_youtube_data.return_value = mock_youtube_data
    mock_summarize_text.return_value = mock_openai_summary

    # Test data - this simulates the user's request to the /summarize endpoint
    test_data = {
        "video_url": "https://www.youtube.com/watch?v=py5byOOHZM8",
        "summary_length": 300,
        "used_model": "gpt-4-mini",
    }

    # Create a dummy token for authentication
    dummy_token = "dummy_token"
    headers = {"Authorization": f"Bearer {dummy_token}"}

    # Mock the authentication service
    mock_auth_service = MagicMock()
    mock_auth_service.authenticate_user_by_token.return_value = MagicMock(user_name="testuser")

    # Make the request to the /summarize endpoint
    response, response_json = mocked_client_post(
        client, mock_auth_service, "/summarize", json=test_data, headers=headers
    )

    # Verify the response status code
    assert response.status_code == 200, "Expected successful response"

    # Assert response structure and content
    assert "summary" in response_json, "Response should contain a 'summary' field"
    assert response_json["summary"] == mock_openai_summary, "Summary should match the mock data"

    assert "word_count" in response_json, "Response should contain a 'word_count' field"
    assert response_json["word_count"] == len(mock_openai_summary.split()), "Word count should match the summary length"

    assert "metadata" in response_json, "Response should contain a 'metadata' field"
    # Compare metadata excluding potentially changing fields
    assert {k: v for k, v in response_json["metadata"].items() if k not in ['view_count', 'like_count']} == \
           {k: v for k, v in mock_youtube_data["metadata"].items() if k not in ['view_count', 'like_count']}, \
           "Metadata should match the mock YouTube data (excluding view_count and like_count)"

    # Verify mock calls
    mock_get_youtube_data.assert_called_once_with("py5byOOHZM8")
    mock_summarize_text.assert_called_once_with(
        " ".join(mock_youtube_data["transcript"]),
        mock_youtube_data["metadata"],
        300,
        "gpt-4-mini",
    )


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
