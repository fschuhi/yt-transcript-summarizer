import pytest
from unittest.mock import patch
from youtube_utils import get_youtube_data
from .test_helpers import get_mock_youtube_data, mock_env_api_keys


@pytest.fixture
def mock_youtube_data():
    """
    Fixture providing mock YouTube data.

    This fixture uses the get_mock_youtube_data() function from test_helpers
    to load pre-defined mock data for YouTube transcripts and metadata.

    :return: A dictionary containing mock transcript and metadata for testing.
    """
    return get_mock_youtube_data()


@patch('youtube_utils.get_youtube_transcript')
@patch('youtube_utils.get_video_metadata')
def test_get_youtube_data(mock_get_video_metadata, mock_get_youtube_transcript, mock_youtube_data, mock_env_api_keys):
    """
    Test the get_youtube_data function from youtube_utils.

    This test uses mock objects to replace the actual YouTube API calls,
    ensuring that the function behaves correctly without making real API requests.

    :param mock_get_video_metadata: Mocked version of get_video_metadata function
    :param mock_get_youtube_transcript: Mocked version of get_youtube_transcript function
    :param mock_youtube_data: Fixture providing mock YouTube data
    :param mock_env_api_keys: Fixture setting dummy API keys in the environment, autouse=True in test_helpers.py
     """
    # Unpack mock_data once
    _mock_youtube_data = mock_youtube_data
    mock_transcript = _mock_youtube_data['transcript']
    mock_metadata = _mock_youtube_data['metadata']

    # Set up our mocks
    mock_get_youtube_transcript.return_value = mock_transcript
    mock_get_video_metadata.return_value = mock_metadata

    # Call the function we're testing
    result = get_youtube_data('py5byOOHZM8')

    # Assert that the result matches our mock data
    assert result == _mock_youtube_data, "The returned data does not match the expected mock data"

    # Verify that our mock functions were called with the correct arguments
    mock_get_youtube_transcript.assert_called_once_with('py5byOOHZM8', include_timestamps=False)
    mock_get_video_metadata.assert_called_once_with('py5byOOHZM8')


if __name__ == "__main__":
    pytest.main()
