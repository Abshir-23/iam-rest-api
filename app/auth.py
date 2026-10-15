"""Hashing av passord og håndtering av JWT-tokener.

Dette er kjernen i identitetslaget: vi lagrer aldri passord i klartekst,
og tilgang bevises med et signert, tidsbegrenset JSON Web Token.
"""
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings
from app.models import Role

# bcrypt er en treg hashalgoritme med salt, standardvalget for passord.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str, role: Role) -> str:
    """Lag et signert JWT som inneholder brukerens identitet og rolle."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": username,      # subjekt: hvem tokenet tilhører
        "role": role.value,   # rollen som RBAC-sjekkene våre bygger på
        "exp": expire,        # utløpstid: tokenet slutter å virke etter dette
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verifiser signatur og utløpstid, og returner innholdet.

    Kaster jwt.InvalidTokenError (eller en underklasse) hvis tokenet er
    tuklet med, har utløpt eller er signert med feil nøkkel.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
