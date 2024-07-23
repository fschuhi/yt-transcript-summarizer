import pytest
from unittest.mock import patch
import os
from youtube_utils import get_youtube_data

import ast


@pytest.fixture
def mock_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data', 'youtube_transcript_cnn_explanation_py5byOOHZM8.txt')
    with open(file_path, 'r') as f:
        content = f.read()
    # Convert the string representation of a dictionary to an actual dictionary
    data_dict = ast.literal_eval(content)
    return data_dict


@pytest.fixture(autouse=True)
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "dummy_api_key")


@patch('youtube_utils.get_youtube_transcript')
@patch('youtube_utils.get_video_metadata')
def test_get_youtube_data(mock_get_video_metadata, mock_get_youtube_transcript, mock_data):
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
    assert result == _mock_data

    # Verify that our mock functions were called
    mock_get_youtube_transcript.assert_called_once_with('py5byOOHZM8', include_timestamps=False)
    mock_get_video_metadata.assert_called_once_with('py5byOOHZM8')
