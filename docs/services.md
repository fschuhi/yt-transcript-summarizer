# Service Descriptions

The YouTube Transcript Summarizer relies on several key services to function:

## YouTube API Service

Location: `services/youtube_api_service.py`

Responsibilities:
- Fetching video transcripts using the YouTube Transcript API
- Retrieving video metadata using the YouTube Data API

Key Methods:
- `get_youtube_transcript(video_id, include_timestamps)`
- `get_video_metadata(video_id)`

## OpenAI API Service

Location: `services/openai_api_service.py`

Responsibilities:
- Generating summaries of video transcripts using OpenAI's language models

Key Methods:
- `summarize_text(text, metadata, max_words, used_model)`

## User Authentication Service

Location: `services/user_auth_service.py`

Responsibilities:
- User registration and authentication
- JWT token generation and verification

Key Methods:
- `register_user(username, email, password)`
- `authenticate_user(identifier, password)`
- `generate_token(user)`
- `authenticate_user_by_token(token)`

These services encapsulate the core business logic of the application, interacting with external APIs and managing user authentication.