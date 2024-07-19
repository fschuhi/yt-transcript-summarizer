from typing import Union, List, Dict

from youtube_transcript_api import YouTubeTranscriptApi


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
        print(f"An error occurred: {str(e)}")
        return []
