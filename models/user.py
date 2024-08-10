from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    last_login_date = Column(DateTime, nullable=True)
    token_issuance_date = Column(DateTime, nullable=True)
    token = Column(String(255), nullable=True)
