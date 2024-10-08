"""Configuration and fixtures for pytest in the FastAPI application."""

import ast
import logging
import os
from datetime import datetime, timedelta
from typing import Dict
from unittest.mock import patch, Mock

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from jose import jwt
from openai import OpenAI

from main import app
from repositories.user_json_repository import UserJsonRepository
from services.user_auth_service import UserAuthService
from scripts import bootstrap_db

logger = logging.getLogger(__name__)


@pytest.fixture
def client(mock_env_variables, mock_token_provider):
    """Create a test client for the FastAPI application with mocked JWT token validation.

    This fixture sets up a controlled environment for testing by using mock
    environment variables and mocking the JWT token validation process.

    Yields: An instance of TestClient for the FastAPI application.
    """
    dummy_username = "testuser"

    with patch("main.get_current_user", return_value=dummy_username):
        with TestClient(app) as test_client:
            logger.info("TestClient created with mocked current user")
            yield test_client


@pytest.fixture(scope="session")
def setup_database():
    """Bootstrap the database before running the tests.

    This fixture is used globally and will only be executed once, before all the tests are run.
    It ensures that the test database is properly set up and migrated.
    """
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        load_dotenv(dotenv_path=os.path.join(project_dir, ".env.test"))
        db_url = os.getenv("DATABASE_URL")

    bootstrap_db.bootstrap_db(
        db_url=db_url,
        script_location=os.path.join(project_dir, "alembic"),
        run_alembic_migrations=True,
        alembic_directory=project_dir,
    )


class MockAPIKeyProvider:
    """Centralized provider for mock API keys used in testing."""

    def __init__(self):
        self.keys = {
            "OPENAI_API_KEY": "dummy_openai_api_key",
            "YOUTUBE_API_KEY": "dummy_youtube_api_key",
            "API_KEY": "dummy_api_key",
        }

    def get_key(self, key_name: str) -> str:
        """Get a mock API key by name."""
        return self.keys[key_name]

    def get_all_keys(self) -> Dict[str, str]:
        """Get all mock API keys."""
        return self.keys.copy()


@pytest.fixture
def mock_api_key_provider():
    """Provide a MockAPIKeyProvider instance.

    Returns: An instance of MockAPIKeyProvider.
    """
    return MockAPIKeyProvider()


@pytest.fixture(autouse=True)
def mock_env_api_keys(monkeypatch, mock_api_key_provider):
    """Set dummy API keys in the environment.

    This fixture is applied automatically to all tests, ensuring that
    all tests use consistent mock API keys instead of real ones.

    Returns: The MockAPIKeyProvider instance for direct access if needed.
    """
    for key, value in mock_api_key_provider.get_all_keys().items():
        monkeypatch.setenv(key, value)
    return mock_api_key_provider


@pytest.fixture
def mock_openai_summary():
    """Load mock OpenAI summary from a file.

    Returns: A string containing the mock summary.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        current_dir, "data", "openai_summary_cnn_explanation_py5byOOHZM8.txt"
    )
    with open(file_path, "r") as f:
        return f.read().strip()


class MockTokenProvider:
    """Centralized provider for mock JWT tokens used in testing."""

    def __init__(self):
        self.secret_key = "test_secret_key"
        self.algorithm = "HS256"
        self.expire_minutes = 30

    def create_access_token(self, data: dict):
        """Create a mock JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def get_token(self, username: str) -> str:
        """Get a mock JWT token for a given username."""
        return self.create_access_token({"sub": username})


@pytest.fixture
def mock_token_provider():
    """Provide a MockTokenProvider instance.

    Returns: An instance of MockTokenProvider.
    """
    return MockTokenProvider()


@pytest.fixture(autouse=True)
def mock_env_variables(monkeypatch, mock_api_key_provider, mock_token_provider):
    """Set dummy environment variables for testing.

    This fixture is applied automatically to all tests, ensuring that
    all tests use consistent mock environment variables instead of real ones.

    Returns: A tuple containing both providers for direct access if needed.
    """
    # Set API keys
    for key, value in mock_api_key_provider.get_all_keys().items():
        monkeypatch.setenv(key, value)

    # Set JWT-related variables
    mock_secret_key = mock_token_provider.secret_key
    monkeypatch.setenv("SECRET_KEY", mock_secret_key)
    print(f"Mock SECRET_KEY set to: {mock_secret_key[:5]}...")  # Print first 5 chars for security

    monkeypatch.setenv("ALGORITHM", mock_token_provider.algorithm)
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(mock_token_provider.expire_minutes))

    return mock_api_key_provider, mock_token_provider


@pytest.fixture
def user_repository():
    """Provide a UserJsonRepository instance for testing.

    Yields: A repository instance for user operations.
    Cleanup: After the test, the temporary JSON file used for testing is removed.
    """
    test_file = "test_users.json"
    repo = UserJsonRepository(test_file)
    yield repo
    # Clean up after test
    if os.path.exists(test_file):
        os.remove(test_file)


@pytest.fixture
def user_auth_service(user_repository, mock_token_provider):
    """Provide a UserAuthService instance for testing.

    Returns: An instance with a mock secret key for testing.
    """
    logger.info(f"Creating UserAuthService with mock secret key: {mock_token_provider.secret_key[:5]}...")
    return UserAuthService(user_repository, secret_key=mock_token_provider.secret_key)


@pytest.fixture
def mock_youtube_data():
    """Fixture providing mock YouTube data.

    Returns: A dictionary containing mock transcript and metadata for testing.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(
        current_dir, "data", "youtube_transcript_cnn_explanation_py5byOOHZM8.txt"
    )
    with open(file_path, "r") as f:
        content = f.read()
    return ast.literal_eval(content)


@pytest.fixture
def mock_youtube_transcript_api():
    """
    Fixture to mock the YouTubeTranscriptApi.

    This fixture uses patch to replace the actual YouTubeTranscriptApi with a mock object,
    allowing us to control its behavior in our tests without making real API calls.
    """
    with patch('services.youtube_api_service.YouTubeTranscriptApi') as mock:
        yield mock


@pytest.fixture
def mock_youtube_build():
    """
    Fixture to mock the googleapiclient.discovery.build function.

    This fixture replaces the actual 'build' function with a mock, allowing us to
    control the behavior of the YouTube API client in our tests.
    """
    with patch('services.youtube_api_service.build') as mock:
        yield mock


@pytest.fixture
def mock_openai_client():
    """
    Fixture to mock OpenAI
    """

    # Create a mock OpenAI client with the correct structure
    mock_client = Mock(spec=OpenAI)
    mock_client.chat = Mock()
    mock_client.chat.completions = Mock()
    mock_client.chat.completions.create = Mock()
    return mock_client

    # Explanation:
    # We're creating a mock object that mimics the structure of the OpenAI client.
    # This allows us to control its behavior and verify how it's called without actually making API requests.
