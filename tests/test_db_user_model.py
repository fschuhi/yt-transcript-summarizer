# conftest.py
import os
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
import tests.db_utils


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


@pytest.mark.db
def test_user_model():
    db_session = create_db_session()
    password = 'hashed_password'
    # Create a new user
    user = User(
        last_login_date=datetime(2023, 5, 1, 10, 30, 0),
        token_issuance_date=datetime(2023, 5, 1, 10, 30, 0),
        token='test_token',
        # password_hash='hashed_password',
        identity_provider='local'
    )
    user.set_password(password)

    # Add the user to the session and commit
    db_session.add(user)
    db_session.commit()

    # Reload the user from the database
    reloaded_user = db_session.query(User).filter_by(user_id=user.user_id).first()

    # Check that the fields match
    assert reloaded_user.last_login_date == user.last_login_date
    assert reloaded_user.token_issuance_date == user.token_issuance_date
    assert reloaded_user.token == user.token
    assert reloaded_user.check_password(password)
    assert reloaded_user.identity_provider == user.identity_provider

    # Delete the user
    db_session.delete(reloaded_user)
    db_session.commit()
