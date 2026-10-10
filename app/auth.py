"""Password hashing and JWT token handling.

This is the core of the identity layer: we never store plaintext passwords,
and access is proven by a signed, time-limited JSON Web Token.
"""
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings
from app.models import Role

# bcrypt is a slow, salted hashing algorithm - the standard choice for passwords.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str, role: Role) -> str:
    """Create a signed JWT carrying the user's identity and role."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": username,      # subject - who the token belongs to
        "role": role.value,   # the claim our RBAC checks rely on
        "exp": expire,        # expiry - the token stops working after this
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verify the signature and expiry, then return the payload.

    Raises jwt.InvalidTokenError (or a subclass) if the token is tampered
    with, expired, or signed with the wrong key.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
