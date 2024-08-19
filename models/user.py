from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255), index=True, unique=True)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=True)
    token_issuance_date = Column(DateTime, nullable=True)
    token = Column(String(255), nullable=True)
    password_hash = Column(String(100), nullable=False)
    identity_provider = Column(String(30), nullable=True, default="local")

    def __init__(
        self, user_id: Optional[int], user_name: str, email: str, password_hash: str
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.email = email
        self.password_hash = password_hash

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "email": self.email,
            "last_login_date": (
                self.last_login_date.isoformat() if self.last_login_date else None
            ),
            "token_issuance_date": (
                self.token_issuance_date.isoformat()
                if self.token_issuance_date
                else None
            ),
            "token": self.token,
            "password_hash": self.password_hash,
            "identity_provider": self.identity_provider,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "User":
        user = cls(
            user_id=data.get("user_id"),
            user_name=data["user_name"],
            email=data["email"],
            password_hash=data["password_hash"],
        )
        user.last_login_date = (
            datetime.fromisoformat(data["last_login_date"])
            if data.get("last_login_date")
            else None
        )
        user.token_issuance_date = (
            datetime.fromisoformat(data["token_issuance_date"])
            if data.get("token_issuance_date")
            else None
        )
        user.token = data.get("token")
        user.identity_provider = data.get("identity_provider", "local")
        return user
