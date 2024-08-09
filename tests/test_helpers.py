import pytest
import os
import ast
from typing import Dict, Any
from datetime import datetime, timedelta
from jose import jwt


class MockAPIKeyProvider:
    """
    Centralized provider for mock API keys used in testing.
    """
    def __init__(self):
        self.keys = {
            "OPENAI_API_KEY": "dummy_openai_api_key",
            "YOUTUBE_API_KEY": "dummy_youtube_api_key",
            "API_KEY": "dummy_api_key"
        }

    def get_key(self, key_name: str) -> str:
        """
        Get a mock API key by name.

        :param key_name: The name of the API key to retrieve.
        :return: The mock API key value.
        :raises KeyError: If the requested key name is not found.
        """
        return self.keys[key_name]

    def get_all_keys(self) -> Dict[str, str]:
        """
        Get all mock API keys.

        :return: A dictionary of all mock API keys.
        """
        return self.keys.copy()


@pytest.fixture
def mock_api_key_provider() -> MockAPIKeyProvider:
    """
    Fixture to provide a MockAPIKeyProvider instance.

    :return: An instance of MockAPIKeyProvider.
    """
    return MockAPIKeyProvider()


@pytest.fixture(autouse=True)
def mock_env_api_keys(monkeypatch, mock_api_key_provider: MockAPIKeyProvider):
    """
    Fixture to set dummy API keys in the environment.

    This fixture uses monkeypatch to set dummy API keys for all tests,
    ensuring that no real API keys are used during testing.

    :param monkeypatch: pytest's monkeypatch fixture for modifying the test environment
    :param mock_api_key_provider: The MockAPIKeyProvider instance
    """
    for key, value in mock_api_key_provider.get_all_keys().items():
        monkeypatch.setenv(key, value)
    return mock_api_key_provider  # Return the provider for direct access if needed


def get_mock_youtube_data() -> Dict[str, Any]:
    """
    Function to load mock YouTube data from a file.

    This function reads a text file containing mock YouTube data (transcript and metadata)
    and converts it into a Python dictionary using ast.literal_eval.

    :return: A dictionary containing mock YouTube data
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', 'youtube_transcript_cnn_explanation_py5byOOHZM8.txt')
    with open(file_path, 'r') as f:
        content = f.read()
    return ast.literal_eval(content)


@pytest.fixture
def mock_openai_summary() -> str:
    """
    Fixture to load mock OpenAI summary from a file.

    This fixture reads a text file containing a mock OpenAI-generated summary.

    :return: A string containing the mock summary
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', 'openai_summary_cnn_explanation_py5byOOHZM8.txt')
    with open(file_path, 'r') as f:
        return f.read().strip()


# Example of how to use parametrization for different API key scenarios
class MockTokenProvider:
    """
    Centralized provider for mock JWT tokens used in testing.
    """

    def __init__(self):
        self.secret_key = "test_secret_key"
        self.algorithm = "HS256"
        self.expire_minutes = 30

    def create_access_token(self, data: dict):
        """
        Create a mock JWT access token.

        :param data: The data to encode in the token.
        :return: A mock JWT token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def get_token(self, username: str) -> str:
        """
        Get a mock JWT token for a given username.

        :param username: The username to create a token for.
        :return: A mock JWT token.
        """
        return self.create_access_token({"sub": username})


@pytest.fixture
def mock_token_provider() -> MockTokenProvider:
    """
    Fixture to provide a MockTokenProvider instance.

    :return: An instance of MockTokenProvider.
    """
    return MockTokenProvider()


@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch, mock_api_key_provider: MockAPIKeyProvider, mock_token_provider: MockTokenProvider):
    """
    Fixture to set dummy environment variables for testing.

    This fixture uses monkeypatch to set dummy API keys and JWT-related variables for all tests,
    ensuring that no real credentials are used during testing.

    :param monkeypatch: pytest's monkeypatch fixture for modifying the test environment
    :param mock_api_key_provider: The MockAPIKeyProvider instance
    :param mock_token_provider: The MockTokenProvider instance
    """
    # Set API keys
    for key, value in mock_api_key_provider.get_all_keys().items():
        monkeypatch.setenv(key, value)

    # Set JWT-related variables
    monkeypatch.setenv("SECRET_KEY", mock_token_provider.secret_key)
    monkeypatch.setenv("ALGORITHM", mock_token_provider.algorithm)
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(mock_token_provider.expire_minutes))

    return mock_api_key_provider, mock_token_provider  # Return both providers for direct access if needed

