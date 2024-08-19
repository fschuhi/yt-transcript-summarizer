import logging
import os
from typing import Callable

from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from services.service_interfaces import IUserRepository
from .user_json_repository import UserJsonRepository
from .user_db_repository import UserDBRepository

logger = logging.getLogger(__name__)


def get_repository(db: Session = Depends(get_db)) -> IUserRepository:
    repository_type = os.getenv("USER_REPOSITORY_TYPE", "json")
    logger.info(f"Creating repository of type: {repository_type}")

    if repository_type == "json":
        return UserJsonRepository('users.json')
    elif repository_type == "postgres":
        return UserDBRepository(db)
    else:
        raise ValueError(f"Invalid USER_REPOSITORY_TYPE: {repository_type}")


def get_repository_provider() -> Callable[..., IUserRepository]:
    repository_type = os.getenv("USER_REPOSITORY_TYPE", "json")
    
    if repository_type == "json":
        return lambda: UserJsonRepository('users.json')
    elif repository_type == "postgres":
        return lambda db: UserDBRepository(db)
    else:
        raise ValueError(f"Invalid USER_REPOSITORY_TYPE: {repository_type}")
