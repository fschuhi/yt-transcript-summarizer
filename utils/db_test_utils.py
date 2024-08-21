"""Database utility functions for testing purposes.

This module provides utility functions for creating database sessions
and initializing the database engine for testing purposes.

TODO:
    - Refactor to use a single engine instance throughout the module.
    - Consider moving the engine initialization to a separate function or module.
    - Evaluate the necessity of the init_engine function and remove if unused.
    - Ensure consistent naming conventions (e.g., 'Session' vs 'session').
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Global engine variable
engine = None


def create_db_session():
    """Create and return a new database session.

    This function initializes the database engine if it hasn't been initialized yet,
    creates a sessionmaker, and returns a new session.

    Returns: A new SQLAlchemy Session object.

    TODO:
        - Consider renaming the local 'engine' variable to avoid shadowing the global 'engine'.
        - Evaluate whether to use the global engine or always create a new one.
    """
    engine = init_engine()
    Session = sessionmaker(bind=engine)  # TODO: Rename 'Session' to 'session' for consistency
    return Session()


def init_engine():
    """Initialize the SQLAlchemy engine object.

    This function creates and returns a new SQLAlchemy engine using the DATABASE_URL
    from environment variables.

    Returns: A SQLAlchemy Engine object.

    TODO:
        - Evaluate whether this function is still needed or if it can be merged with create_db_session.
        - Consider caching the engine to avoid creating a new one for each call.
    """
    db_url = os.getenv("DATABASE_URL")
    global engine
    engine = create_engine(db_url)
    return engine
