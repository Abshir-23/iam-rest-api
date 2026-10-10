"""A tiny in-memory user store.

Kept deliberately simple so the focus stays on the identity and access-control
logic. In a real system this would be a database (and the seed users would not
exist). Swapping this module for a real DB layer would not change the API.
"""
from app.auth import hash_password
from app.models import Role, UserInDB

# Seeded accounts so the API is usable immediately. Passwords are hashed at
# startup - the plaintext only lives here for demo convenience.
_users: dict[str, UserInDB] = {}


def _seed() -> None:
    seed_data = [
        ("admin", "admin12345", Role.admin),
        ("alice", "alice12345", Role.user),
    ]
    for username, password, role in seed_data:
        _users[username] = UserInDB(
            username=username,
            role=role,
            hashed_password=hash_password(password),
        )


def get_user(username: str) -> UserInDB | None:
    return _users.get(username)


def add_user(user: UserInDB) -> None:
    _users[user.username] = user


def delete_user(username: str) -> bool:
    return _users.pop(username, None) is not None


def list_users() -> list[UserInDB]:
    return list(_users.values())


_seed()
