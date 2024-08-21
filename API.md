# API Documentation

This document outlines the API endpoints for the YouTube Transcript Summarizer application.

## Endpoints

### Health Check

```
GET /health
```

Checks the health status of the API.

Response:
- Status Code: `200 OK`
- Body: `{"status": "healthy"}`

### Root Endpoint

```
GET /
```

This endpoint is forbidden and returns a `403` status code.

Response:
- Status Code: `403 Forbidden`
- Body: `{"detail": "Access to this endpoint is forbidden"}`

### User Registration

```
POST /register
```

Registers a new user.

Request Body:
```
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

Response:
- Status Code: `200 OK`
- Body: `{"message": "User registered successfully"}`

Errors:
- `400 Bad Request`: If registration fails due to existing username/email or other errors.

### User Authentication

```
POST /token
```

Authenticates a user and generates an access token.

Request Body (form-data):
- `username: string`
- `password: string`

Response:
- Status Code: `200 OK`
- Body:
```
  {
    "access_token": "string",
    "token_type": "bearer"
  }
```

Errors:
- `401 Unauthorized`: If login fails due to invalid credentials.
- `500 Internal Server Error`: For unexpected errors during login.

### Summarize YouTube Video

```
POST /summarize
```

Summarizes a YouTube video transcript.

Request Body:
```
{
  "video_url": "string",
  "summary_length": "integer",
  "used_model": "string"
}
```

Headers:
- Authorization: `Bearer {access_token}`

Response:
- Status Code: `200 OK`
- Body:
```
{
    "summary": "string",
    "word_count": "integer",
    "metadata": {
      "title": "string",
      "description": "string",
      "channel_title": "string",
      "channel_id": "string",
      "publish_date": "string",
      "view_count": "integer",
      "like_count": "integer",
      "comment_count": "integer"
    }
  }
```

  Errors:
- `400 Bad Request`: If the YouTube URL is invalid or the transcript cannot be retrieved.
- `401 Unauthorized`: If the authentication token is missing or invalid.
- `500 Internal Server Error`: For unexpected errors during summarization.

## Authentication

Most endpoints require authentication using a Bearer token. To authenticate, include the following header in your requests:

Authorization: `Bearer {your_access_token}`

You can obtain an access token by using the `/token` endpoint.