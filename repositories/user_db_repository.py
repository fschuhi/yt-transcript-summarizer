from typing import List, Optional, cast

from sqlalchemy.orm import Session

from models.user import User
from services.service_interfaces import IUserRepository


class UserDBRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_by_identifier(self, identifier: str) -> Optional[User]:
        return self.session.query(User).filter_by(user_name=identifier).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()

    def get_all(self) -> List[User]:
        return cast(List[User], self.session.query(User).all())

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
