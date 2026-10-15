"""Et lite brukerlager i minnet.

Holdt bevisst enkelt slik at fokuset blir på logikken for identitet og
tilgangskontroll. I et ekte system ville dette vært en database (og
startbrukerne ville ikke funnes). Å bytte ut denne modulen med et ekte
databaselag ville ikke endret API-et.
"""
from app.auth import hash_password
from app.models import Role, UserInDB

# Ferdige kontoer slik at API-et kan brukes med en gang. Passordene hashes
# ved oppstart, klarteksten finnes bare her for å gjøre demoen enkel.
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
