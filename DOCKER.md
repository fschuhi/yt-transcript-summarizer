# Docker Configuration

This document details the Docker setup for the YouTube Transcript Summarizer project.

## Dockerfile

The `Dockerfile` defines the main application container:

- Base image: Python 3.9-slim
- Installs project dependencies from `requirements.txt`
- Exposes ports 8000 (FastAPI) and 5432 (PostgreSQL)
- Runs the FastAPI application using Uvicorn

## docker-compose.yml

This file orchestrates the main services:

- `fastapi`: The main application service.
- `postgres`: PostgreSQL database service.
- `pgadmin`: pgAdmin service for database management.

Environment variables are loaded from `.env` file.

## docker-compose-dev.yml

This file is used for development purposes and includes services for:

- Creating the development database
- Bootstrapping the database
- Running Alembic migrations

## docker-compose-test.yml

This file is used for running tests in a containerized environment:

- Sets up a test database
- Runs pytest

## wait-for-it.sh

A utility script used in Docker Compose files to wait for services (like PostgreSQL) to be ready before starting dependent services.

## Usage

1. Build the containers: `docker-compose build`
2. Start the services: `docker-compose up`
3. Run development tasks: `docker-compose -f docker-compose-dev.yml run <service_name>`
4. Run tests: `docker-compose -f docker-compose-test.yml run test`

For more detailed commands, refer to the Makefile in the project root.