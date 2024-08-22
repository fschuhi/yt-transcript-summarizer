# Deployment Guide

This guide outlines the steps to deploy the YouTube Transcript Summarizer.

## Prerequisites

- Docker and Docker Compose installed on the host machine
- Access to a PostgreSQL database
- OpenAI API key
- YouTube Data API key

## Deployment Steps

1. Clone the repository:
   git clone https://github.com/yourusername/yt-transcript-summarizer.git
   cd yt-transcript-summarizer

2. Set up environment variables:
   - Copy .env.example to .env
   - Fill in all required variables in .env

3. Build Docker images:
   docker-compose build

4. Start the services:
   docker-compose up -d

5. Run database migrations:
   docker-compose exec fastapi alembic upgrade head

6. Access the API:
   The API will be available at http://localhost:8000

## Monitoring and Maintenance

- Logs can be viewed using:
  docker-compose logs

- To update the application:
  git pull
  docker-compose build
  docker-compose up -d

- Database backups should be performed regularly

## Scaling

For increased load, consider:
- Using a production-grade WSGI server like Gunicorn
- Implementing a load balancer
- Scaling the database (e.g., read replicas, sharding)

## Security Considerations

- Keep all API keys and secrets secure
- Regularly update dependencies
- Use HTTPS in production
- Implement rate limiting and other API security measures

For more detailed information on production deployment best practices, consult the FastAPI documentation and Docker best practices guides.