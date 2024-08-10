import os
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command
import logging
from logging.config import fileConfig
from sqlalchemy import text
import argparse


def initialize_alembic_logger():
    alembic_cfg = Config("alembic.ini")
    fileConfig(alembic_cfg.config_file_name)
    return logging.getLogger('alembic')


def bootstrap_db(db_url: str, script_location: str = '', run_migrations: bool = False):
    """
    Sets up a test database, including:
    1. Checking if the database exists
    2. Dropping the database if it exists
    3. Creating an empty database
    4. Running all Alembic migrations on the database
    """
    # 1. Check if the test database exists
    logger = initialize_alembic_logger()

    db_name = db_url.rsplit('/', 1)[-1]
    db_server_url = db_url.replace('/' + db_name, '/postgres')
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
    if run_migrations:
        logger.info("Running Alembic migrations...")
        alembic_cfg = Config("alembic.ini")
        if script_location:
            alembic_cfg.set_main_option('script_location', script_location)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(alembic_cfg, 'head')


if __name__ == "__main__":
    # Example usage
    parser = argparse.ArgumentParser(description="Bootstrap a database")

    logger = initialize_alembic_logger()

    # Add the named parameters as arguments
    parser.add_argument("--db-url", dest="db_url", required=False, default=os.getenv("DATABASE_URL"))
    parser.add_argument("--script-location", dest="script_location", required=False, default='')
    parser.add_argument("--run-migrations", dest="run_migrations", required=False, default=True)

    # Parse the arguments
    args = parser.parse_args()

    # Create a dictionary from the named parameters
    params = vars(args)
    logger.info(params)

    # this is bad however I couldn't the parser to accept a string and convert it to boolean
    if isinstance(params['run_migrations'], str):
        run_migrations = params['run_migrations'][0] == 'T'
    else:
        run_migrations = params['run_migrations']

    bootstrap_db(params['db_url'], params['script_location'], run_migrations)
