import pytest
import os
import ast


def get_mock_youtube_data():
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
def mock_openai_summary():
    """
    Fixture to load mock OpenAI summary from a file.

    This fixture reads a text file containing a mock OpenAI-generated summary.

    :return: A string containing the mock summary
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', 'openai_summary_cnn_explanation_py5byOOHZM8.txt')
    with open(file_path, 'r') as f:
        return f.read().strip()


@pytest.fixture(autouse=True)
def mock_env_api_keys(monkeypatch):
    """
    Fixture to set dummy API keys in the environment.

    This fixture uses monkeypatch to set dummy API keys for all tests,
    ensuring that no real API keys are used during testing.

    :param monkeypatch: pytest's monkeypatch fixture for modifying the test environment
    """
    monkeypatch.setenv("OPENAI_API_KEY", "dummy_openai_api_key")
    monkeypatch.setenv("YOUTUBE_API_KEY", "dummy_youtube_api_key")
    monkeypatch.setenv("API_KEY", "dummy_api_key")
