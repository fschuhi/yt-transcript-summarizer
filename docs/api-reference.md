# API Reference

This document provides an overview of the available API endpoints in the YouTube Transcript Summarizer.

## Endpoints

### Health Check

GET /health
- Description: Checks the health status of the API
- Response: {"status": "healthy"}

### User Registration

POST /register
- Description: Registers a new user
- Request Body: {"username": string, "email": string, "password": string}
- Response: {"message": "User registered successfully"}

### User Authentication

POST /token
- Description: Authenticates a user and returns an access token
- Request Body: {"username": string, "password": string}
- Response: {"access_token": string, "token_type": "bearer"}

### Summarize Video

POST /summarize
- Description: Summarizes a YouTube video transcript
- Authentication: Required
- Request Body: {"video_url": string, "summary_length": integer, "used_model": string}
- Response: {"summary": string, "word_count": integer, "metadata": object}

For detailed information on request/response formats and error handling, refer to the API documentation available at http://localhost:8000/docs when the server is running.