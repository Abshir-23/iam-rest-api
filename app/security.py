"""Authentication and authorization dependencies.

- authentication: who are you?  -> get_current_user
- authorization:  what may you do?  -> require_role
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth import decode_access_token
from app.database import get_user
from app.models import Role, UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Decode the bearer token and load the matching user.

    This is the authentication gate: any endpoint that depends on it can only
    be reached with a valid, unexpired token.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_error
    except jwt.InvalidTokenError:
        raise credentials_error

    user = get_user(username)
    if user is None:
        raise credentials_error
    return user


def require_role(*allowed_roles: Role):
    """Build a dependency that only lets the given roles through.

    Usage: Depends(require_role(Role.admin))
    This is the authorization gate - least privilege enforced per endpoint.
    """
    def checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return checker
