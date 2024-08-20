"""
Unit tests for the YouTubeAPIService class.

This module contains tests to ensure the proper functioning of the YouTubeAPIService,
particularly its abilities to fetch video transcripts and metadata using the YouTube API.
"""

from unittest.mock import Mock
from services.youtube_api_service import YouTubeAPIService


def test_get_youtube_data2(mock_youtube_transcript_api, mock_youtube_build, mock_youtube_data):
    """
    Test the get_youtube_transcript and get_video_metadata methods of YouTubeAPIService.

    This test ensures that the YouTubeAPIService correctly interacts with both the
    YouTube Transcript API and the YouTube Data API to fetch transcript and metadata.

    Args:
        mock_youtube_transcript_api: A mock object replacing YouTubeTranscriptApi.
        mock_youtube_build: A mock object replacing the 'build' function for the YouTube API.
        mock_youtube_data: A dictionary containing mock YouTube video data,
            including transcript and metadata.
    """
    # Set up mocks for the YouTube Transcript API
    mock_youtube_transcript_api.get_transcript.return_value = mock_youtube_data["transcript"]

    # Set up mocks for the YouTube Data API
    mock_youtube = Mock()
    mock_youtube_build.return_value = mock_youtube
    mock_videos = Mock()
    mock_youtube.videos.return_value = mock_videos
    mock_list = Mock()
    mock_videos.list.return_value = mock_list

    # Mock the response from the YouTube Data API
    mock_list.execute.return_value = {
        "items": [{
            "snippet": {
                "title": mock_youtube_data["metadata"]["title"],
                "description": mock_youtube_data["metadata"]["description"],
                "channelTitle": mock_youtube_data["metadata"]["channel_title"],
                "channelId": mock_youtube_data["metadata"]["channel_id"],
                "publishedAt": mock_youtube_data["metadata"]["publish_date"],
            },
            "statistics": {
                "viewCount": str(mock_youtube_data["metadata"]["view_count"]),
                "likeCount": str(mock_youtube_data["metadata"]["like_count"]),
                "commentCount": str(mock_youtube_data["metadata"]["comment_count"]),
            }
        }]
    }

    # Explanation of the mock setup:
    # 1. We create a chain of mock objects that mimic the structure of the YouTube API client.
    # 2. We set up the execute() method to return our predefined mock data.
    # 3. This allows us to control what data is "returned" by the API without making real API calls.

    # Create YouTubeAPIService instance with mocked dependencies
    service = YouTubeAPIService(
        youtube_transcript_api=mock_youtube_transcript_api,
        youtube_build=mock_youtube_build
    )

    # Test get_youtube_transcript
    transcript = service.get_youtube_transcript("dummy_video_id")
    assert transcript == mock_youtube_data["transcript"]

    # Test get_video_metadata
    metadata = service.get_video_metadata("dummy_video_id")
    assert metadata == mock_youtube_data["metadata"]

    # Verify that our mock functions were called correctly
    mock_youtube_transcript_api.get_transcript.assert_called_once_with("dummy_video_id")
    mock_youtube_build.assert_called_once_with("youtube", "v3", developerKey=service.api_key)
    mock_videos.list.assert_called_once_with(part="snippet,statistics", id="dummy_video_id")

    # Explanation of assertions:
    # 1. We check if the returned transcript and metadata match our mock data.
    # 2. We verify that the mock objects were called with the expected arguments.
    # 3. This ensures that our service is interacting with the APIs correctly, even though we're using mocks.
