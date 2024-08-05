# conftest.py
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def db_engine():
    # Load environment variables from .env.test file
    env_vars = {
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB")
    }

    # Create SQLAlchemy engine
    db_url = f"postgresql://{env_vars['POSTGRES_USER']}:{env_vars['POSTGRES_PASSWORD']}@{env_vars['POSTGRES_HOST']}:{env_vars['POSTGRES_PORT']}/{env_vars['POSTGRES_DB']}"
    engine = create_engine(db_url)

    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


# test_db_connection.py
@pytest.mark.db
def test_database_connection(db_session):
    # Test the database connection by executing a simple SQL query
    result = db_session.execute(text('SELECT 1')).fetchone()
    assert result[0] == 1
