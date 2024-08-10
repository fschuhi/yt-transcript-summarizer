# conftest.py
import os
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from models.user import UserRepository
import tests.db_utils as db_utils


def create_db_session():
    db_url = os.getenv('DATABASE_URL')
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def test_user_set_password():
    password = 'hashed_password'
    user = User(
        last_login_date=datetime(2023, 5, 1, 10, 30, 0),
        token_issuance_date=datetime(2023, 5, 1, 10, 30, 0),
        token='test_token',
        identity_provider='local'
    )
    user.set_password(password)
    assert user.check_password(password)


def create_default_user(password: str) -> User:
    # Create a new user
    user = User(
        user_name='summaria@summaria.com',
        last_login_date=datetime(2023, 5, 1, 10, 30, 0),
        token_issuance_date=datetime(2023, 5, 1, 10, 30, 0),
        token='test_token',
        # password_hash='hashed_password',
        identity_provider='local'
    )
    user.set_password(password)
    return user


@pytest.mark.db
def test_user_model():
    db_session = db_utils.create_db_session()
    password = 'hashed_password'
    user = create_default_user(password)
    user_repository = UserRepository(db_session)

    # Add the user to the session and commit
    user_repository.create(user)

    # Reload the user from the database
    reloaded_user = user_repository.get_by_id(user_id=user.user_id)

    # Check that the fields match
    assert isinstance(reloaded_user, User)
    assert reloaded_user.user_name == user.user_name
    assert reloaded_user.last_login_date == user.last_login_date
    assert reloaded_user.token_issuance_date == user.token_issuance_date
    assert reloaded_user.token == user.token
    assert reloaded_user.check_password(password)
    assert reloaded_user.identity_provider == user.identity_provider

    # Delete the user
    user_repository.delete(reloaded_user)


@pytest.mark.db
def test_user_repository_get_by_user_name():
    db_session = db_utils.create_db_session()
    password = 'hashed_password'
    user = create_default_user(password)
    user_repository = UserRepository(db_session)

    # Add the user to the session and commit
    user_repository.create(user)
    reloaded_user = user_repository.get_by_user_name(user_name=user.user_name)
    assert isinstance(reloaded_user, User)
    assert reloaded_user.user_name == user.user_name
