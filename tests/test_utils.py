"""Utility functions for testing the FastAPI application."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from .conftest import client


def mocked_client_post(
        client: TestClient,
        mock_auth_service,
        endpoint: str,
        data=None,
        json=None,
        headers=None,
):
    mock_repo = MagicMock()

    # Create a mock UserAuthService class that returns our mock_auth_service
    mock_user_auth_service_class = MagicMock(return_value=mock_auth_service)

    with patch("repositories.repository_provider.get_repository", return_value=mock_repo):
        with patch("services.dependencies.UserAuthService", mock_user_auth_service_class):
            response = client.post(endpoint, json=json, data=data, headers=headers)

    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    return response, response.json()