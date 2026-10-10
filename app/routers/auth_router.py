from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_access_token, hash_password, verify_password
from app.database import add_user, get_user
from app.models import Token, UserCreate, UserInDB, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(new_user: UserCreate):
    """Create a new account. Fails if the username is taken."""
    if get_user(new_user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    user = UserInDB(
        username=new_user.username,
        role=new_user.role,
        hashed_password=hash_password(new_user.password),
    )
    add_user(user)
    return UserPublic(username=user.username, role=user.role)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Exchange username + password for a JWT access token.

    The generic error message avoids telling an attacker whether it was the
    username or the password that was wrong (user enumeration protection).
    """
    user = get_user(form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(username=user.username, role=user.role)
    return Token(access_token=token)
