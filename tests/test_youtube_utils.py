import pytest
from unittest.mock import patch
import os
from youtube_utils import get_youtube_data
import ast


@pytest.fixture
def mock_data():
    """
    Fixture to load mock data from a file.

    This fixture reads a text file containing mock YouTube data (transcript and metadata)
    and converts it into a Python dictionary using ast.literal_eval.

    :return: A dictionary containing mock YouTube data
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', 'youtube_transcript_cnn_explanation_py5byOOHZM8.txt')
    with open(file_path, 'r') as f:
        content = f.read()
    # Convert the string representation of a dictionary to an actual dictionary
    data_dict = ast.literal_eval(content)
    return data_dict


@pytest.fixture(autouse=True)
def mock_env_api_key(monkeypatch):
    """
    Fixture to set a dummy YouTube API key in the environment.

    This fixture uses monkeypatch to set a dummy API key for all tests,
    ensuring that no real API key is used during testing.

    :param monkeypatch: pytest's monkeypatch fixture for modifying the test environment
    """
    monkeypatch.setenv("YOUTUBE_API_KEY", "dummy_api_key")


@patch('youtube_utils.get_youtube_transcript')
@patch('youtube_utils.get_video_metadata')
def test_get_youtube_data(mock_get_video_metadata, mock_get_youtube_transcript, mock_data):
    """
    Test the get_youtube_data function from youtube_utils.

    This test uses mock objects to replace the actual YouTube API calls,
    ensuring that the function behaves correctly without making real API requests.

    :param mock_get_video_metadata: Mocked version of get_video_metadata function
    :param mock_get_youtube_transcript: Mocked version of get_youtube_transcript function
    :param mock_data: Fixture providing mock YouTube data
    """
    # Unpack mock_data once
    _mock_data = mock_data
    mock_transcript = _mock_data['transcript']
    mock_metadata = _mock_data['metadata']

    # Set up our mocks
    mock_get_youtube_transcript.return_value = mock_transcript
    mock_get_video_metadata.return_value = mock_metadata

    # Call the function we're testing
    result = get_youtube_data('py5byOOHZM8')

    # Assert that the result matches our mock data
    assert result == _mock_data, "The returned data does not match the expected mock data"

    # Verify that our mock functions were called with the correct arguments
    mock_get_youtube_transcript.assert_called_once_with('py5byOOHZM8', include_timestamps=False)
    mock_get_video_metadata.assert_called_once_with('py5byOOHZM8')


if __name__ == "__main__":
    pytest.main()
