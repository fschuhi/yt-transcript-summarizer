from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import bcrypt
from typing import Optional, List, Type
from sqlalchemy.orm import Session

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    # we don't define user_name as primary key since we want to be able to change it if necessary
    user_name = Column(String(255), index=True, unique=True)
    last_login_date = Column(DateTime, nullable=True)
    token_issuance_date = Column(DateTime, nullable=True)
    token = Column(String(255), nullable=True)
    password_hash = Column(String(100), nullable=False)
    identity_provider = Column(String(30), nullable=True, default='local')

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def set_token(self, token: str):
        self.token = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_token(self, token: str) -> bool:
        return bcrypt.checkpw(token.encode('utf-8'), self.token.encode('utf-8'))


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_by_user_name(self, user_name: str) -> Optional[User]:
        return self.session.query(User).filter_by(user_name=user_name).first()

    def get_all(self) -> list[Type[User]]:
        return self.session.query(User).all()

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def update(self, user: User) -> User:
        self.session.merge(user)
        self.session.commit()
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
