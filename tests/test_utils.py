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
    with patch("main.get_repository", return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch("main.UserAuthService", return_value=mock_auth_service):
            response = client.post(endpoint, json=json, data=data, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    return response, response.json()
