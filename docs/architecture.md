# Architecture Overview

The YouTube Transcript Summarizer is built using a modular architecture with the following key components:

1. FastAPI Web Server
2. Authentication Service
3. YouTube API Service
4. OpenAI API Service
5. Database Layer (PostgreSQL)

## Component Interaction

1. The FastAPI server handles incoming HTTP requests.
2. Requests are authenticated using the Authentication Service.
3. For summarization requests:
   a. The YouTube API Service retrieves video transcripts and metadata.
   b. The OpenAI API Service generates summaries using AI models.
4. User data is stored and retrieved using the Database Layer.

## Key Technologies

- FastAPI: Web framework for building APIs
- SQLAlchemy: ORM for database operations
- Alembic: Database migration tool
- Pydantic: Data validation and settings management
- Python-jose: JWT token handling
- Docker: Containerization for development and deployment

## Project Structure

- `main.py`: FastAPI application entry point
- `models/`: Database models
- `repositories/`: Data access layer
- `services/`: Business logic implementation
- `utils/`: Utility functions
- `tests/`: Test suite
- `alembic/`: Database migration scripts

This architecture ensures separation of concerns, making the codebase modular and maintainable.