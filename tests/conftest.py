import os
import pytest
from utils import bootstrap_db
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def log_repository_type():
    repository_type = os.getenv("USER_REPOSITORY_TYPE", "json")
    logger.info(f"\n*** Running tests with repository type: {repository_type} ***\n")


@pytest.fixture(scope="session")
def setup_database():
    """
    Fixture that bootstraps the database before running the tests.
    This fixture will only be executed once, before all the tests are run.
    """

    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        load_dotenv(dotenv_path=os.path.join(project_dir, '.env.test'))
        db_url = os.getenv('DATABASE_URL')

    bootstrap_db.bootstrap_db(db_url=db_url,
                              script_location=os.path.join(project_dir, 'alembic'),
                              run_alembic_migrations=True,
                              alembic_directory=project_dir)