from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_access_token, hash_password, verify_password
from app.database import add_user, get_user
from app.models import Token, UserCreate, UserInDB, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(new_user: UserCreate):
    """Opprett en ny konto. Feiler hvis brukernavnet er tatt."""
    if get_user(new_user.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Brukernavnet finnes allerede",
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
    """Bytt brukernavn + passord mot et JWT-tilgangstoken.

    Den generelle feilmeldingen gjør at en angriper ikke får vite om det var
    brukernavnet eller passordet som var feil (beskyttelse mot brukeropptelling).
    """
    user = get_user(form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Feil brukernavn eller passord",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(username=user.username, role=user.role)
    return Token(access_token=token)
