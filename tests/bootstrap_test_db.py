import os
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command
import logging
from logging.config import fileConfig
from sqlalchemy import text


def bootstrap_database(db_url: str, script_location: str = ''):
    """
    Sets up a test database, including:
    1. Checking if the test database exists
    2. Dropping the test database if it exists
    3. Creating an empty test database
    4. Running all Alembic migrations on the test database
    """
    # 1. Check if the test database exists
    alembic_cfg = Config("alembic.ini")
    fileConfig(alembic_cfg.config_file_name)
    logger = logging.getLogger('alembic')

    db_name = db_url.rsplit('/', 1)[-1]
    db_server_url = db_url.replace(db_name, 'postgres')
    logger.info(f'bootstrapping database {db_name} on {db_server_url}')

    engine = create_engine(db_server_url, isolation_level='AUTOCOMMIT')
    try:
        with engine.connect() as conn:
            conn.execute(text(f"DROP DATABASE IF EXISTS {db_name} WITH (FORCE);"))
            conn.execute(text(f"CREATE DATABASE {db_name};"))
            logger.info(f"Created the database '{db_name}'.")

    except Exception as e:
        logger.error(f"Error occured: {e}")

    # 4. Run all Alembic migrations on the test database
    logger.info("Running Alembic migrations...")
    if script_location:
        alembic_cfg.set_main_option('script_location', script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, 'head')


if __name__ == "__main__":
    # Example usage
    test_db_url = os.getenv("DATABASE_URL")
    bootstrap_database(test_db_url)
