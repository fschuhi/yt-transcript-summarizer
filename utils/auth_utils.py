import bcrypt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
import os
from typing import Optional

from jose import jwt

logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 12 * 60  # 12 hours


class AuthenticationUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_access_token(data: dict, secret_key: str = DEFAULT_SECRET_KEY, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def generate_jwt_token(username: str, secret_key: str = DEFAULT_SECRET_KEY) -> str:
        logger.info(f"Generating JWT token with SECRET_KEY: {secret_key[:5]}...")  # Log first 5 chars for security
        return AuthenticationUtils.create_access_token(data={"sub": username}, secret_key=secret_key)

    @staticmethod
    def verify_jwt_token(token: str, secret_key: str = DEFAULT_SECRET_KEY) -> Optional[str]:
        try:
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except jwt.JWTError:
            return None


# For backwards compatibility, you might want to keep these function definitions:
def hash_password(password: str) -> str:
    return AuthenticationUtils.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return AuthenticationUtils.verify_password(password, hashed_password)


def create_access_token(data: dict, secret_key: str = DEFAULT_SECRET_KEY, expires_delta: Optional[timedelta] = None) -> str:
    return AuthenticationUtils.create_access_token(data, secret_key, expires_delta)


def generate_jwt_token(username: str, secret_key: str = DEFAULT_SECRET_KEY) -> str:
    return AuthenticationUtils.generate_jwt_token(username, secret_key)