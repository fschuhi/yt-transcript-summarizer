from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
import bcrypt

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    last_login_date = Column(DateTime, nullable=True)
    token_issuance_date = Column(DateTime, nullable=True)
    token = Column(String(255), nullable=True)
    password_hash = Column(String(100), nullable=False)
    identity_provider = Column(String(30), nullable=True, default='local')

    def set_password(self, password):
       self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))