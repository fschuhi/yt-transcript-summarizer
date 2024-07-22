import pytest
from unittest.mock import patch, MagicMock
from youtube_utils import get_youtube_data


def mock_get_transcript(video_id):
    return [
        {'text': 'This is a mock transcript.', 'start': 0.0, 'duration': 2.0},
        {'text': 'It simulates a real YouTube transcript.', 'start': 2.0, 'duration': 3.0}
    ]


@patch('youtube_utils.get_youtube_transcript')
@patch('youtube_utils.get_video_metadata')
def test_get_youtube_data(mock_get_video_metadata, mock_get_youtube_transcript):
    # Set up mock returns
    mock_get_youtube_transcript.return_value = ['This is a mock transcript.', 'It simulates a real YouTube transcript.']
    mock_get_video_metadata.return_value = {
        'title': 'Mock Video',
        'channel_title': 'Mock Channel',
        'view_count': 1000
    }

    video_id = "dQw4w9WgXcQ"  # Example YouTube video ID
    result = get_youtube_data(video_id)

    # Assert the result is a dictionary
    assert isinstance(result, dict)

    # Assert the result contains 'metadata' and 'transcript' keys
    assert 'metadata' in result
    assert 'transcript' in result

    # Assert the transcript is a list of strings
    assert isinstance(result['transcript'], list)
    assert all(isinstance(item, str) for item in result['transcript'])
    assert len(result['transcript']) > 0

    # Assert the content of the transcript
    assert result['transcript'][0] == 'This is a mock transcript.'
    assert result['transcript'][1] == 'It simulates a real YouTube transcript.'

    # Assert metadata contains expected keys
    assert 'title' in result['metadata']
    assert 'channel_title' in result['metadata']
    assert 'view_count' in result['metadata']

    # Assert the mocks were called correctly
    mock_get_youtube_transcript.assert_called_once_with(video_id, include_timestamps=False)
    mock_get_video_metadata.assert_called_once_with(video_id)