from fastapi import Depends, HTTPException
from starlette import status

from services.user_auth_service import UserAuthService
from services.service_interfaces import IUserAuthService
from repositories.repository_provider import get_repository, IUserRepository
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_auth_service2(repo: IUserRepository = Depends(get_repository)) -> IUserAuthService:
    return UserAuthService(repo)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: IUserAuthService = Depends(get_user_auth_service2)
) -> str:
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = auth_service.authenticate_user_by_token(token)
        if user is None:
            raise credentials_exception
        return user.user_name
    except Exception:
        raise credentials_exception
