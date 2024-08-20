"""Utilities for fetching YouTube video transcripts and metadata."""

import logging
import os
import re
from typing import Dict, List, Union, Optional

from dotenv import load_dotenv
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
# noinspection PyPackageRequirements
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi

# Suppress googleapiclient.discovery_cache info messages
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if YOUTUBE_API_KEY:
    print(f"YouTube API Key: {YOUTUBE_API_KEY[:5]}...")  # Print first 5 chars for security
else:
    print("YouTube API Key not found in environment variables.")


def get_youtube_transcript(
        video_id: str, include_timestamps: bool = True
) -> Union[List[Dict[str, Union[str, float]]], List[str]]:
    """Retrieve the transcript for a YouTube video.

    Args:
        video_id: The YouTube video ID.
        include_timestamps: Whether to include timestamps in the output.
    Returns: List of transcript segments, with or without timestamps.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript if include_timestamps else [segment["text"] for segment in transcript]
    except Exception as e:
        print(f"Error fetching transcript: {str(e)}")
        return []


def get_video_metadata(video_id: str) -> Dict[str, Union[str, int]]:
    """Retrieve metadata for a YouTube video using the YouTube Data API.

    Args:
        video_id: The YouTube video ID.
    Returns: Dictionary containing video metadata.
    """
    if not YOUTUBE_API_KEY:
        print("YouTube API key not found in environment variables.")
        return {}

    try:
        # Build the YouTube API client
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # Fetch video details
        video_response = youtube.videos().list(part="snippet,statistics", id=video_id).execute()

        if not video_response["items"]:
            raise ValueError(f"No video found with id: {video_id}")

        video_data = video_response["items"][0]
        snippet = video_data["snippet"]
        statistics = video_data["statistics"]

        # Extract relevant metadata
        return {
            "title": snippet["title"],
            "description": snippet["description"],
            "channel_title": snippet["channelTitle"],
            "channel_id": snippet["channelId"],
            "publish_date": snippet["publishedAt"],
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
        }

    except HttpError as e:
        print(f"HTTP error occurred: {str(e)}")
        return {}
    except Exception as e:
        print(f"Error fetching video metadata: {str(e)}")
        return {}


def get_youtube_data(
        video_id: str,
) -> Dict[str, Union[List[str], Dict[str, Union[str, int]]]]:
    """Retrieve both transcript and metadata for a YouTube video.

    Args:
        video_id: The YouTube video ID.
    Returns: Dictionary containing the transcript and metadata.
    """
    transcript = get_youtube_transcript(video_id, include_timestamps=False)
    metadata = get_video_metadata(video_id)
    return {"transcript": transcript, "metadata": metadata}


def extract_video_id(input_string: str) -> Optional[str]:
    """Extract the YouTube video ID from various URL formats or direct ID input.

    Args:
        input_string: The input string containing a YouTube URL or video ID.
    Returns: The extracted video ID, or None if no valid ID is found.
    """
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)

    if re.match(r"^[a-zA-Z0-9_-]{11}$", input_string):
        return input_string

    return None
