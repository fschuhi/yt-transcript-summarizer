"""Tests for YouTube utility functions."""

from unittest.mock import patch

import pytest

# These imports are used indirectly through fixtures
from tests.conftest import MockAPIKeyProvider, mock_api_key_provider, mock_env_api_keys
from utils import youtube_utils
from utils.youtube_utils import get_youtube_data


@patch.object(youtube_utils, "get_youtube_transcript")
@patch.object(youtube_utils, "get_video_metadata")
def test_get_youtube_data(
    mock_get_video_metadata,
    mock_get_youtube_transcript,
    mock_youtube_data,
    mock_env_api_keys,
):
    """Test the get_youtube_data function from youtube_utils.

    Uses mock objects to replace YouTube API calls and verifies correct behavior
    of the function without making real API requests.
    """
    # Unpack mock data
    _mock_youtube_data = mock_youtube_data
    mock_transcript = _mock_youtube_data["transcript"]
    mock_metadata = _mock_youtube_data["metadata"]

    # Set up mocks
    mock_get_youtube_transcript.return_value = mock_transcript
    mock_get_video_metadata.return_value = mock_metadata

    # Call the function we're testing
    result = get_youtube_data("py5byOOHZM8")

    # Verify the result
    assert result == _mock_youtube_data, "Returned data doesn't match expected mock data"

    # Verify that our mock functions were called correctly
    mock_get_youtube_transcript.assert_called_once_with(
        "py5byOOHZM8", include_timestamps=False
    )
    mock_get_video_metadata.assert_called_once_with("py5byOOHZM8")


if __name__ == "__main__":
    pytest.main()
