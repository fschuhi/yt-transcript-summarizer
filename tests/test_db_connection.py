import pytest
from sqlalchemy import create_engine, text

import tests.db_utils as db_utils


# test_db_connection.py
@pytest.mark.db
def test_database_connection(setup_database):
    # Test the database connection by executing a simple SQL query
    session = None
    try:
        session = db_utils.create_db_session()
        result = session.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
    finally:
        session.close()
