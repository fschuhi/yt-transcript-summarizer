import pytest
from unittest.mock import patch

from utils import youtube_utils
from utils.youtube_utils import get_youtube_data

# The following imports are required even though they appear unused.
# MockAPIKeyProvider and mock_api_key_provider are used indirectly
# through the mock_env_api_keys fixture, which is essential for setting up
# the test environment with mock API keys. Removing these imports will
# cause test failures due to missing fixtures.
# see also ((UHAEBLK))
# noinspection PyUnresolvedReferences
from tests.conftest import MockAPIKeyProvider, mock_api_key_provider, mock_env_api_keys


@patch.object(youtube_utils, "get_youtube_transcript")
@patch.object(youtube_utils, 'get_video_metadata')
def test_get_youtube_data(mock_get_video_metadata, mock_get_youtube_transcript, mock_youtube_data, mock_env_api_keys):
    """
    Test the get_youtube_data function from youtube_utils.

    This test uses mock objects to replace the actual YouTube API calls,
    ensuring that the function behaves correctly without making real API requests.

    :param mock_get_video_metadata: Mocked version of get_video_metadata function
    :param mock_get_youtube_transcript: Mocked version of get_youtube_transcript function
    :param mock_youtube_data: Fixture providing mock YouTube data
    :param mock_env_api_keys: Fixture setting dummy API keys in the environment, autouse=True in test_helpers.py (TODO: review)
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
