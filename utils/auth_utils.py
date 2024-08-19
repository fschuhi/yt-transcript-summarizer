import bcrypt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from typing import Optional

# noinspection PyPackageRequirements
from jose import jwt

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
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
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def generate_jwt_token(username: str) -> str:
        return AuthenticationUtils.create_access_token(data={"sub": username})

    @staticmethod
    def verify_jwt_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return AuthenticationUtils.create_access_token(data, expires_delta)


def generate_jwt_token(username: str) -> str:
    return AuthenticationUtils.generate_jwt_token(username)
