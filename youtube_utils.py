from typing import Union, List, Dict
from youtube_transcript_api import YouTubeTranscriptApi

# noinspection PyPackageRequirements
from googleapiclient.discovery import build

# noinspection PyPackageRequirements
from googleapiclient.errors import HttpError

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the YouTube API key from environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
print(f"YouTube API Key: {YOUTUBE_API_KEY[:5]}...")  # Print first 5 characters for security


def get_youtube_transcript(video_id: str, include_timestamps: bool = True) -> Union[
    List[Dict[str, Union[str, float]]], List[str]]:
    """
    Retrieves the transcript for a YouTube video using youtube_transcript_api.

    :param video_id: The YouTube video ID
    :param include_timestamps: Whether to include timestamps in the output
    :return: A list of transcript segments, either with or without timestamps
    """
    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        if include_timestamps:
            return transcript
        else:
            return [segment["text"] for segment in transcript]
    except Exception as e:
        print(f"An error occurred while fetching transcript: {str(e)}")
        return []


def get_video_metadata(video_id: str) -> Dict[str, Union[str, int]]:
    """
    Retrieves metadata for a YouTube video using the YouTube Data API.

    :param video_id: The YouTube video ID
    :return: A dictionary containing video metadata
    """
    if not YOUTUBE_API_KEY:
        print("YouTube API key not found in environment variables.")
        return {}

    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Call the videos().list method to retrieve video details
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if not video_response['items']:
            raise ValueError(f"No video found with id: {video_id}")

        video_data = video_response['items'][0]
        snippet = video_data['snippet']
        statistics = video_data['statistics']

        # Extract relevant metadata
        metadata = {
            'title': snippet['title'],
            'description': snippet['description'],
            'channel_title': snippet['channelTitle'],
            'channel_id': snippet['channelId'],
            'publish_date': snippet['publishedAt'],
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
        }

        return metadata

    except HttpError as e:
        print(f"An HTTP error occurred: {str(e)}")
        return {}
    except Exception as e:
        print(f"An error occurred while fetching video metadata: {str(e)}")
        return {}


def get_youtube_data(video_id: str) -> Dict[str, Union[List[str], Dict[str, Union[str, int]]]]:
    """
    Retrieves both transcript and metadata for a YouTube video.

    :param video_id: The YouTube video ID
    :return: A dictionary containing the transcript and metadata
    """
    transcript = get_youtube_transcript(video_id, include_timestamps=False)
    metadata = get_video_metadata(video_id)

    return {
        'transcript': transcript,
        'metadata': metadata
    }
