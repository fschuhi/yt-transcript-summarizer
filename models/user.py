from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    # we don't define user_name as primary key since we want to be able to change it if necessary
    user_name = Column(String(255), index=True, unique=True)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=True)
    token_issuance_date = Column(DateTime, nullable=True)
    token = Column(String(255), nullable=True)
    password_hash = Column(String(100), nullable=False)
    identity_provider = Column(String(30), nullable=True, default='local')

    def __init__(self, user_id: Optional[int], user_name: str, email: str, password_hash: str):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.password_hash = password_hash

# Remove the UserRepository class if it's in this file, as it should be in a separate repository file
