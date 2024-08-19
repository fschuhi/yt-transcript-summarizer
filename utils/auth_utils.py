"""Authentication utilities for password hashing, JWT token generation, and verification.

This module provides utilities for user authentication, including password hashing,
JWT token creation, and token verification. It uses bcrypt for password hashing
and jose for JWT operations.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from jose import jwt

logger = logging.getLogger(__name__)

load_dotenv()

DEFAULT_SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12 * 60  # 12 hours


class AuthenticationUtils:
    """Utility class providing static methods for authentication-related operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: The plain-text password to hash.
        Returns: The hashed password as a string.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hashed version.

        Args:
            password: The plain-text password to verify.
            hashed_password: The hashed password to compare against.
        Returns: True if the password matches the hash, False otherwise.
        """
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_access_token(
        data: dict,
        secret_key: str = DEFAULT_SECRET_KEY,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token.

        Args:
            data: The payload to encode in the token.
            secret_key: The secret key to use for encoding. Defaults to DEFAULT_SECRET_KEY.
            expires_delta: The expiration time for the token. Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.
        Returns: The encoded JWT token.
        """
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
        """Generate a JWT token for a given username.

        Args:
            username: The username to encode in the token.
            secret_key: The secret key to use for encoding. Defaults to DEFAULT_SECRET_KEY.
        Returns: The generated JWT token.
        """
        logger.info(f"Generating JWT token with SECRET_KEY: {secret_key[:5]}...")
        return AuthenticationUtils.create_access_token(
            data={"sub": username}, secret_key=secret_key
        )

    @staticmethod
    def verify_jwt_token(token: str, secret_key: str = DEFAULT_SECRET_KEY) -> Optional[str]:
        """Verify a JWT token and extract the username.

        Args:
            token: The JWT token to verify.
            secret_key: The secret key to use for decoding. Defaults to DEFAULT_SECRET_KEY.
        Returns: The username extracted from the token if valid, None otherwise.
        """
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
    """Hash a password using bcrypt. (Wrapper for AuthenticationUtils.hash_password)"""
    return AuthenticationUtils.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hashed version. (Wrapper for AuthenticationUtils.verify_password)"""
    return AuthenticationUtils.verify_password(password, hashed_password)


def create_access_token(
    data: dict,
    secret_key: str = DEFAULT_SECRET_KEY,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token. (Wrapper for AuthenticationUtils.create_access_token)"""
    return AuthenticationUtils.create_access_token(data, secret_key, expires_delta)


def generate_jwt_token(username: str, secret_key: str = DEFAULT_SECRET_KEY) -> str:
    """Generate a JWT token for a given username. (Wrapper for AuthenticationUtils.generate_jwt_token)"""
    return AuthenticationUtils.generate_jwt_token(username, secret_key)
