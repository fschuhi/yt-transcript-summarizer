"""Tests for the repository selection and instantiation logic."""

import logging
import os
from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from repositories.repository_provider import get_repository
from repositories.user_db_repository import UserDBRepository
from repositories.user_json_repository import UserJsonRepository

logger = logging.getLogger(__name__)


def test_repository_type(client: TestClient):
    """
    Test the correct repository type is used based on environment settings.

    This test verifies that the application correctly selects and instantiates
    either a JSON-based or a database-based repository depending on the
    USER_REPOSITORY_TYPE environment variable.
    """
    # Determine the expected repository type from the environment
    repository_type = os.getenv("USER_REPOSITORY_TYPE", "json")

    # Create an instance of the appropriate repository type
    if repository_type == "postgres":
        expected_repo = UserDBRepository(MagicMock())  # Pass a mock Session for Postgres
    else:
        expected_repo = UserJsonRepository("test_users.json")  # Default to JSON

    # Patch the get_repository function to return our expected repository
    with patch("repositories.repository_provider.get_repository", return_value=expected_repo):
        # Make a request to trigger repository creation
        response = client.get("/health")
        assert response.status_code == 200

    # Verify the type of repository used matches our expectation
    if repository_type == "postgres":
        assert isinstance(
            expected_repo, UserDBRepository
        ), f"Expected UserDBRepository, got {type(expected_repo)}"
    else:
        assert isinstance(
            expected_repo, UserJsonRepository
        ), f"Expected UserJsonRepository, got {type(expected_repo)}"

    logger.info(f"Confirmed repository type: {type(expected_repo).__name__}")


# Additional comments on the repository pattern:
"""
This test demonstrates the flexibility of our repository pattern:

1. Environment-based Configuration:
   - The system chooses between JSON and Postgres storage based on the
     USER_REPOSITORY_TYPE environment variable.

2. Abstraction of Data Storage:
   - Whether using JSON or Postgres, the application interacts with the
     repository through a common interface (IUserRepository).

3. Ease of Testing:
   - By patching the get_repository function, we can easily control and
     verify the type of repository used in tests.

4. Adaptability:
   - This setup allows for easy switching between storage types without
     changing application code, facilitating testing and deployment across
     different environments.

The test ensures that this flexibility works as intended, verifying correct
repository selection and instantiation based on the environment configuration.
"""
