# Dependency Injection Explanation

The YouTube Transcript Summarizer uses FastAPI's dependency injection system to manage service dependencies and promote loose coupling between components.

## Key Concepts

1. Dependency Providers: Functions that create and return service instances
2. Dependency Injection: FastAPI automatically injects dependencies into route handlers

## Main Dependencies

1. User Authentication Service
   - Provider: `get_user_auth_service2`
   - Usage: Handles user authentication and token generation

2. Current User
   - Provider: `get_current_user`
   - Usage: Retrieves the authenticated user for protected routes

3. YouTube API Service
   - Provider: `get_youtube_service`
   - Usage: Interacts with YouTube APIs for transcript and metadata retrieval

4. OpenAI API Service
   - Provider: `get_openai_service`
   - Usage: Generates summaries using OpenAI's language models

## Implementation

Dependencies are defined in `services/dependencies.py`. For example:

```python
def get_youtube_service() -> YouTubeAPIService:
    return YouTubeAPIService(
        youtube_transcript_api=YouTubeTranscriptApi,
        youtube_build=build
    )
```

In route handlers, dependencies are injected as function parameters:

```python
@app.post("/summarize")
async def summarize_endpoint(
    summarize_request: SummarizeRequest,
    current_user: str = Depends(get_current_user),
    youtube_service: YouTubeAPIService = Depends(get_youtube_service),
    openai_service: OpenAIAPIService = Depends(get_openai_service)
):
    # Function implementation
```

This approach allows for easy testing and flexibility in service implementation.


