"""Implementation of YouTube API service."""

import os
import re
from typing import Dict, List, Union, Optional

from dotenv import load_dotenv
# noinspection PyPackageRequirements
from googleapiclient.discovery import build
# noinspection PyPackageRequirements
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi

from services.service_interfaces import IYouTubeAPIService

load_dotenv()


class YouTubeAPIService(IYouTubeAPIService):
    def __init__(self, youtube_transcript_api=None, youtube_build=None):
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        if self.api_key:
            print(f"YouTube API Key: {self.api_key[:5]}...")
        else:
            print("YouTube API Key not found in environment variables.")

        self.youtube_transcript_api = youtube_transcript_api or YouTubeTranscriptApi
        self.youtube_build = youtube_build or build

    def get_youtube_transcript(
            self, video_id: str, include_timestamps: bool = True
    ) -> Union[List[Dict[str, Union[str, float]]], List[str]]:
        try:
            transcript = self.youtube_transcript_api.get_transcript(video_id)
            return transcript if include_timestamps else [segment["text"] for segment in transcript]
        except Exception as e:
            print(f"Error fetching transcript: {str(e)}")
            return []

    def get_video_metadata(self, video_id: str) -> Dict[str, Union[str, int]]:
        if not self.api_key:
            print("YouTube API key not found in environment variables.")
            return {}

        try:
            youtube = self.youtube_build("youtube", "v3", developerKey=self.api_key)
            video_response = youtube.videos().list(part="snippet,statistics", id=video_id).execute()

            if not video_response["items"]:
                raise ValueError(f"No video found with id: {video_id}")

            video_data = video_response["items"][0]
            snippet = video_data["snippet"]
            statistics = video_data["statistics"]

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

        except KeyError as e:
            print(f"Error fetching video metadata: {str(e)}")
            return {}
        except HttpError as e:
            print(f"HTTP error occurred: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error fetching video metadata: {str(e)}")
            return {}
