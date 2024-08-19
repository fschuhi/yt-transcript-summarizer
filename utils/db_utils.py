"""Database utility module for managing SQLAlchemy sessions and handling CI environments."""

import logging
import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

# Determine if we're running in a Continuous Integration (CI) environment
IN_CI = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize engine and SessionLocal to None; they'll be set up if not in CI
engine = None
SessionLocal = None

logger.info(f"IN_CI={IN_CI}")

if not IN_CI:
    # Set up the database connection for non-CI environments
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL is not set (we are not running in the CI environment)")

    # Create the SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Create a sessionmaker, which will be used to create database sessions
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a transactional scope around a series of operations.

    This function is a generator that yields database sessions. It handles both CI
    and non-CI environments differently:
    - In CI: It yields a mock session to avoid actual database operations.
    - In non-CI: It yields a real database session and ensures it's closed after use.

    Yields:
        Session: Either a mock session (in CI) or a real SQLAlchemy session.

    Usage:
        This function is typically used with FastAPI's dependency injection system.
        It ensures that each request gets its own database session, which is then
        closed when the request is complete, regardless of whether an exception occurred.
    """
    if IN_CI:
        # In CI environment, yield a mock session to avoid actual DB operations
        class MockSession:
            def close(self):
                # Mock close method to mimic real session behavior
                pass

        yield MockSession()
    else:
        # In non-CI environment, create and yield a real database session
        db = SessionLocal()
        try:
            yield db
        finally:
            # Ensure the database session is closed after the request is processed
            db.close()

# Flow of operations:
# 1. When this module is imported, it determines if it's running in a CI environment.
# 2. If not in CI, it sets up the database engine and session maker.
# 3. The get_db() function is used as a dependency in FastAPI route functions.
# 4. When a request comes in, get_db() either:
#    a) Yields a mock session (in CI) to avoid real DB operations, or
#    b) Creates a new database session, yields it, and ensures it's closed after use.
# 5. This approach allows for easy testing in CI environments while providing
#    proper database sessions in production or development environments.
