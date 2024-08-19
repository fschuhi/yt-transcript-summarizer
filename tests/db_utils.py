import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = None


# Create the SQLAlchemy engine and session
def create_db_session():
    engine = init_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_engine():
    """Initialize the SQLAlchemy engine object."""
    db_url = os.getenv("DATABASE_URL")
    global engine
    engine = create_engine(db_url)
    return engine
