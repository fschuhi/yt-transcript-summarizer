from abc import ABC, abstractmethod
from typing import Optional, List, Type
from models.user import User


class IUserService(ABC):
    @abstractmethod
    def register_user(self, username: str, email: str, password: str) -> User:
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        pass

    @abstractmethod
    def authenticate_user_by_token(self, token: str) -> Optional[User]:
        pass

    @abstractmethod
    def generate_token(self, user: User) -> str:
        pass

    @abstractmethod
    def get_user(self, username: str) -> Optional[User]:
        pass


class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_user_name(self, user_name: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user: User) -> None:
        pass