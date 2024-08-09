import bcrypt
from typing import Optional
from jose import jwt

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_jwt_token(username: str) -> str:
    payload = {'username': username}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token