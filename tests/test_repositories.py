import os
import logging
from unittest.mock import patch, MagicMock

from starlette.testclient import TestClient

from repositories.user_json_repository import UserJsonRepository
from repositories.user_db_repository import UserDBRepository

logger = logging.getLogger(__name__)


def test_repository_type(client: TestClient):
    repository_type = os.getenv("USER_REPOSITORY_TYPE", "json")

    # Create an instance of the appropriate repository type
    if repository_type == "postgres":
        expected_repo = UserDBRepository(MagicMock())  # Pass a mock Session
    else:
        expected_repo = UserJsonRepository('test_users.json')

    with patch('main.get_repository', return_value=expected_repo):
        response = client.get("/health")
        assert response.status_code == 200

    # Verify the type of repository used
    if repository_type == "postgres":
        assert isinstance(expected_repo, UserDBRepository), f"Expected UserDBRepository, got {type(expected_repo)}"
    else:
        assert isinstance(expected_repo, UserJsonRepository), f"Expected UserJsonRepository, got {type(expected_repo)}"

    logger.info(f"Confirmed repository type: {type(expected_repo).__name__}")

