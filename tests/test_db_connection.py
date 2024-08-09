# conftest.py
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def db_engine():
    db_url = os.getenv('DATABASE_URL')
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
