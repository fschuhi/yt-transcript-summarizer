from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from .conftest import client


def mock_repo_and_auth_service(repo_return_value=None, auth_service_return_value=None):
    """
    Create mock objects for repository and authentication service.

    :param repo_return_value: Value to be returned by the mock repository
    :param auth_service_return_value: Value to be returned by the mock auth service
    :return: Tuple of (mock_repo, mock_auth_service)
    """
    mock_repo = MagicMock()
    if repo_return_value is not None:
        mock_repo.return_value = repo_return_value

    mock_auth_service = MagicMock()
    if auth_service_return_value is not None:
        mock_auth_service.return_value = auth_service_return_value

    return mock_repo, mock_auth_service


def mocked_client_post(client: TestClient, mock_auth_service, endpoint: str, data=None, json=None, headers=None):
    mock_repo = MagicMock()
    with patch('main.get_repository', return_value=mock_repo):
        # Patch the UserAuthService to return our mock service
        with patch('main.UserAuthService', return_value=mock_auth_service):
            response = client.post(endpoint, json=json, data=data, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    return response, response.json()
