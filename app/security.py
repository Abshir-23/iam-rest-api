"""Avhengigheter for autentisering og autorisasjon.

- autentisering: hvem er du?          -> get_current_user
- autorisasjon:  hva har du lov til?  -> require_role
"""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth import decode_access_token
from app.database import get_user
from app.models import Role, UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Dekod bearer-tokenet og hent brukeren det gjelder.

    Dette er autentiseringsporten: alle endepunkter som er avhengige av den,
    kan bare nås med et gyldig token som ikke har utløpt.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kunne ikke validere innloggingsopplysningene",
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
    """Lag en avhengighet som bare slipper gjennom de oppgitte rollene.

    Bruk: Depends(require_role(Role.admin))
    Dette er autorisasjonsporten: minste privilegium håndheves per endepunkt.
    """
    def checker(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Du har ikke tilgang til å utføre denne handlingen",
            )
        return current_user

    return checker
