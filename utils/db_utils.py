import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

load_dotenv()

# Check if we're running in a CI environment
IN_CI = os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true"

DATABASE_URL = os.getenv("DATABASE_URL")

engine = None
SessionLocal = None

logger.info(f"IN_CI={IN_CI}")
if not IN_CI:
    if DATABASE_URL is None:
        raise ValueError(
            "DATABASE_URL is not set (we are not running in the CI environment)"
        )
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    if IN_CI:
        # Yield a mock session or a null object
        class MockSession:
            def close(self):
                pass

        yield MockSession()
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()