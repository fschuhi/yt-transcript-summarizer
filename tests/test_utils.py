# tests/test_utils.py

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app


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


def mock_auth_and_get_token(mock_auth_service):
    """
    Mock authentication and token generation.

    :param mock_auth_service: Mocked authentication service
    :return: Mocked token
    """
    mock_user = MagicMock()
    mock_auth_service.authenticate_user.return_value = mock_user
    mock_auth_service.generate_token.return_value = "dummy_token"
    return "dummy_token"
