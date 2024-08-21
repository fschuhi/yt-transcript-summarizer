# YouTube Transcript Summarizer

A tool to summarize YouTube videos using their transcripts and AI models.

## Features

- Summarize YouTube videos using AI models
- Adjustable summary length
- Support for multiple ChatGPT models
- User authentication and management
- PostgreSQL database integration
- Docker support for easy development and deployment

## Quick Start

1. Clone the repository:
   `git clone https://github.com/yourusername/yt-transcript-summarizer.git`
   `cd yt-transcript-summarizer`

2. Set up your environment:
   - Copy `.env.example` to `.env` and fill in your API keys
   - For development, use `.env.dev`
   - For testing, use `.env.test`

3. Build and run with Docker:
   `make build_container`
   `make run_containers`

4. Access the API at `http://localhost:8000`

## Configuration

Essential environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `YOUTUBE_API_KEY`: Your YouTube Data API key
- `SECRET_KEY`: Secret key for JWT token generation and verification
- `DATABASE_URL`: PostgreSQL connection string
- `USER_REPOSITORY_TYPE`: either json or postgres, depending on what type of repository is used to back the user data
- `PROJECT_DIR`: necessary for Docker to mount parts of the project locally

See `.env.example` for all required variables.

## Development

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Make (optional, for using Makefile commands)

### Local Development

1. Install dependencies:
   `pip install -r requirements.txt`

2. Run the FastAPI server:
   `python main.py`

### Using Docker

Use the provided Makefile for common tasks:

- `make build_container`: Build Docker containers
- `make run_containers`: Start services
- `make stop_containers`: Stop services
- `make clean_containers`: Remove all containers and volumes
- `make run_tests`: Run the test suite
- `make run_fastapi`: Start the FastAPI server

For database operations:
- `make dev_create_db`: Create development database
- `make dev_bootstrap_db`: Bootstrap the database
- `make dev_new_migration`: Create a new Alembic migration
- `make dev_run_migrations`: Run Alembic migrations

## Project Structure

- `main.py`: FastAPI application entry point
- `models/`: Database models
- `repositories/`: Data access layer
- `services/`: Business logic
- `utils/`: Utility functions
- `tests/`: Test suite
- `alembic/`: Database migration scripts

## Docker Setup

Key Docker files:
- `Dockerfile`: Main application container definition
- `docker-compose.yml`: Main services orchestration
- `docker-compose-dev.yml`: Development environment configuration
- `docker-compose-test.yml`: Test environment configuration

For detailed Docker information, see `DOCKER.md`.

## Testing

Run tests using:
`make run_tests`

or for local testing:
`pytest`

## API Documentation

API documentation is available at http://localhost:8000/docs when the server is running.

## Contributing

This is a personal learning project, but suggestions and feedback are welcome. Feel free to open an issue or submit a pull request.

## License

MIT