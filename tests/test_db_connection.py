import pytest
from sqlalchemy import text

import utils.db_test_utils as db_utils


@pytest.mark.db
def test_database_connection(setup_database):
    """Test the database connection by executing a simple SQL query."""
    session = None
    try:
        # Create a new database session
        session = db_utils.create_db_session()

        # Execute a simple query to check if the connection is working
        result = session.execute(text("SELECT 1")).fetchone()

        # Assert that the query returns the expected result
        assert result[0] == 1, "Database connection test failed"
    finally:
        # Ensure the session is closed even if an exception occurs
        if session:
            session.close()

# Additional notes:
# - @pytest.mark.db: Marks this test as a database-related test
# - setup_database: Fixture that sets up the database before running the test
# - The test uses a simple "SELECT 1" query to verify database connectivity
# - This test helps ensure that the application can establish a working connection to the database
