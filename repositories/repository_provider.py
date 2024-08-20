"""Provider module for user repositories, handling both database and JSON storage options."""

import logging
import os
from typing import Callable

from fastapi import Depends
from sqlalchemy.orm import Session

from utils.db_utils import get_db
from services.service_interfaces import IUserRepository
from .user_db_repository import UserDBRepository
from .user_json_repository import UserJsonRepository

logger = logging.getLogger(__name__)

# Determine if we're running in a Continuous Integration (CI) environment
IN_CI = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"


def get_repository(db: Session = Depends(get_db)) -> IUserRepository:
    """
    Provide the appropriate user repository based on the environment and configuration.

    This function determines which type of repository to use (JSON or Postgres)
    based on the environment variables and whether we're in a CI environment.

    Args:
        db: SQLAlchemy database session (injected by FastAPI).
    Returns: An instance of IUserRepository (either UserJsonRepository or UserDBRepository).
    Raises: ValueError if an invalid repository type is specified.
    """
    # Determine repository type: use 'json' in CI, otherwise use the environment variable
    repository_type = "json" if IN_CI else os.getenv("USER_REPOSITORY_TYPE", "json")
    logger.info(f"Creating repository of type: {repository_type}")
    if repository_type == "json":
        return UserJsonRepository("users.json")
    elif repository_type == "postgres":
        # Check if we have a real database session (not in CI)
        if not hasattr(db, "execute"):
            logger.warning("Using JSON repository due to mock session in CI")
            return UserJsonRepository("users.json")
        return UserDBRepository(db)
    else:
        raise ValueError(f"Invalid USER_REPOSITORY_TYPE: {repository_type}")


def get_repository_provider() -> Callable[..., IUserRepository]:
    """
    Provide a factory function for creating user repositories.

    This function returns a callable that can be used to create the appropriate
    repository instance. It's useful for scenarios where dependency injection
    might not be directly available.

    Returns: A callable that creates and returns an IUserRepository instance.
    Raises: ValueError if an invalid repository type is specified.
    """
    repository_type = "json" if IN_CI else os.getenv("USER_REPOSITORY_TYPE", "json")

    if repository_type == "json":
        return lambda: UserJsonRepository("users.json")
    elif repository_type == "postgres":
        return lambda db: UserDBRepository(db)
    else:
        raise ValueError(f"Invalid USER_REPOSITORY_TYPE: {repository_type}")

# Flow of operations:
# 1. When this module is imported, it determines if it's running in a CI environment.
# 2. The get_repository function is the main entry point for obtaining a repository instance:
#    a) It checks the environment to determine which repository type to use.
#    b) For JSON repositories, it creates and returns a UserJsonRepository instance.
#    c) For Postgres repositories:
#       - In non-CI environments, it creates and returns a UserDBRepository instance.
#       - In CI environments or if a mock session is detected, it falls back to UserJsonRepository.
# 3. The get_repository_provider function creates a factory for repository instances:
#    a) It returns a lambda function that, when called, creates the appropriate repository.
#    b) This is useful for scenarios where you need to defer repository creation.
# 4. Both functions handle the 'json' and 'postgres' repository types, throwing an error for invalid types.
# 5. This setup allows for flexible repository usage across different environments:
#    - CI environments always use JSON storage for simplicity and isolation.
#    - Production/development can use either JSON or Postgres based on configuration.
#    - The system gracefully handles cases where database sessions might not be available.

# Key benefits of this approach:
# - Separation of concerns: Repository creation is isolated from business logic.
# - Flexibility: Easy to switch between storage types without changing application code.
# - Testability: Facilitates easy mocking and testing in CI environments.
# - Scalability: Provides a pattern that can be extended for additional repository types.
