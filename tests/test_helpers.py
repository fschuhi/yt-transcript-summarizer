import pytest
import os
import ast
from typing import Dict, Any


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
@pytest.fixture(params=[
    {"OPENAI_API_KEY": "test_openai_key", "YOUTUBE_API_KEY": "test_youtube_key", "API_KEY": "test_api_key"},
    {"OPENAI_API_KEY": "dummy_openai_api_key", "YOUTUBE_API_KEY": "dummy_youtube_api_key", "API_KEY": "dummy_api_key"}
])
def parametrized_api_keys(request, monkeypatch):
    """
    Parametrized fixture for testing different API key scenarios.

    :param request: pytest request object containing the parameter
    :param monkeypatch: pytest's monkeypatch fixture
    :return: A dictionary of API keys for the current test scenario
    """
    for key, value in request.param.items():
        monkeypatch.setenv(key, value)
    return request.param
