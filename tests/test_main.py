import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from .test_helpers import get_mock_youtube_data, mock_openai_summary, mock_env_api_keys
from .test_helpers import mock_api_key_provider


@pytest.fixture
def client(mock_env_api_keys, mock_api_key_provider):
    """
    Fixture to create a test client for the FastAPI application with mocked API key validation.

    This fixture does the following:
    1. Uses the mock_env_api_keys fixture to set up mock environment variables.
    2. Uses the mock_api_key_provider to get a consistent dummy API key.
    3. Patches the get_api_key_value function to return the dummy API key.
    4. Creates and yields a TestClient instance for the FastAPI app.

    :param mock_env_api_keys: Fixture that sets up mock environment variables (including API keys).
    :param mock_api_key_provider: Fixture that provides a MockAPIKeyProvider instance.
    :return: A TestClient instance for the FastAPI application.
    """
    # We patch main.get_api_key_value instead of main.get_api_key because:
    # 1. get_api_key is a dependency that uses get_api_key_value internally.
    # 2. By patching get_api_key_value, we control the source of the API key without
    #    modifying the validation logic in get_api_key.
    # 3. This approach allows us to test the actual get_api_key function's logic.

    # We use mock_api_key_provider.get_key("API_KEY") to ensure consistency
    # between the mocked environment variables and the patched get_api_key_value.
    with patch('main.get_api_key_value', return_value=mock_api_key_provider.get_key("API_KEY")):
        # The 'with' statement is used for context management in Python.
        # It ensures that resources are properly set up and cleaned up.

        # TestClient is a special client provided by FastAPI for testing.
        # It allows us to make requests to our FastAPI application without running a server.
        with TestClient(app) as test_client:
            # The 'yield' keyword is used in Python generators and, in this case, in fixtures.
            # It does the following:
            # 1. It provides the test_client to the test function.
            # 2. It allows the test to run.
            # 3. After the test is complete, it resumes here to do any cleanup if necessary.
            # 4. In this case, it ensures that the TestClient is properly closed after the test.
            #
            # Additionally:
            # 1. It allows the TestClient to be created with the patched get_api_key_value.
            # 2. It keeps the TestClient and the patch active for the duration of each test.
            # 3. It ensures proper cleanup after each test, preventing potential side effects between tests.
            yield test_client
        # After yielding, any cleanup code would go here (if needed).
        # The TestClient and the patch are automatically cleaned up due to the 'with' statements.


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_invalid_api_key(client):
    headers = {"X-API-Key": "invalid_key"}
    response = client.post("/login", headers=headers)
    assert response.status_code == 403


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
        "used_model": "gpt-4o-mini"
    }

    # Make request
    headers = {"X-API-Key": "dummy_api_key"}
    response = client.post("/summarize", json=test_data, headers=headers)

    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
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
        "gpt-4o-mini"
    )


if __name__ == "__main__":
    pytest.main()
