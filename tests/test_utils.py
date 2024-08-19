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
    """
    Perform a mocked POST request to the FastAPI application.

    This function sets up a controlled environment for testing POST requests by:
    1. Mocking the repository used by the application.
    2. Patching the UserAuthService with a provided mock.
    3. Executing the POST request using the test client.

    The mocking ensures that the test is isolated from the actual database and authentication service.

    Args:
        client (TestClient): The FastAPI test client.
        mock_auth_service: A mock object representing the UserAuthService.
        endpoint (str): The API endpoint to send the POST request to.
        data (dict, optional): Form data to send with the request.
        json (dict, optional): JSON data to send with the request.
        headers (dict, optional): Headers to send with the request.

    Returns: tuple: A tuple containing the response object and the parsed JSON response.

    Usage:
        This function is typically used in test functions to simulate POST requests
        while controlling the behavior of the repository and authentication service.

    Flow of operations:
    1. Create a mock repository.
    2. Patch the 'get_repository' function to return the mock repository.
    3. Patch the UserAuthService with the provided mock_auth_service.
    4. Execute the POST request using the test client.
    5. Print response details for debugging purposes.
    6. Return the response object and parsed JSON.
    """
    mock_repo = MagicMock()
    with patch("main.get_repository", return_value=mock_repo):
        with patch("main.UserAuthService", return_value=mock_auth_service):
            response = client.post(endpoint, json=json, data=data, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    return response, response.json()
