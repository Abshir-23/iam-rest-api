# IAM REST API

A secure REST API built with FastAPI, demonstrating the two halves of identity and access management: **authentication** (proving who you are with JWT) and **authorization** (controlling what you can do with role-based access control).

## What it does

- Users log in with a username and password and receive a signed **JWT access token**
- Passwords are never stored in plaintext, they are hashed with **bcrypt**
- Every protected endpoint requires a valid, unexpired token
- Endpoints enforce **least privilege** through roles: a normal `user` cannot reach `admin`-only routes
- Tokens are time-limited and signature-verified, so a tampered or expired token is rejected

## Endpoints

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| `POST` | `/auth/register` | Public | Create a new account |
| `POST` | `/auth/login` | Public | Exchange credentials for a JWT |
| `GET`  | `/users/me` | Any logged-in user | Read your own profile |
| `GET`  | `/users` | Admin only | List all accounts |
| `DELETE` | `/users/{username}` | Admin only | Delete an account (not your own) |
| `GET`  | `/` | Public | Health check |

## How access control works

Two FastAPI dependencies do the work:

- **`get_current_user`** decodes the bearer token, verifies its signature and expiry, and loads the matching user. This is the *authentication* gate, no valid token, no entry.
- **`require_role(Role.admin)`** builds on that and checks the role claim inside the token. This is the *authorization* gate, it returns **403 Forbidden** when an authenticated user lacks the required role.

The role lives inside the signed token, so it cannot be changed by the client without breaking the signature.

## Project structure

```
app/
  config.py          # settings (secret key, token expiry)
  models.py          # Pydantic schemas and the Role enum
  auth.py            # password hashing + JWT create/decode
  database.py        # in-memory user store (swap for a real DB)
  security.py        # get_current_user + require_role dependencies
  routers/
    auth_router.py   # /auth/register, /auth/login
    users_router.py  # /users/me, /users, /users/{username}
  main.py            # app entry point
tests/
  test_api.py        # 10 tests covering auth + RBAC
```

## Running it

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

### Seeded accounts

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin12345` | admin |
| `alice` | `alice12345` | user |

### Quick try

```bash
# Log in and grab a token
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=admin&password=admin12345"

# Use the token on an admin-only endpoint
curl http://127.0.0.1:8000/users \
  -H "Authorization: Bearer <paste-token-here>"
```

## Tests

```bash
pytest -q
```

Covers successful login, wrong password, missing token, tampered token, a normal user being blocked from admin routes (403), admin access, registration, duplicate usernames, and deletion rules.

## Security notes

- `SECRET_KEY` defaults to a placeholder for local use. In production it must come from an environment variable or a secrets manager (for example Azure Key Vault), never committed to source control.
- The in-memory store and seeded accounts are for demonstration. A real deployment would use a database and would not ship with default credentials.
- Login returns the same generic error for a wrong username or a wrong password, which avoids leaking whether an account exists (user enumeration).

## Tech

Python · FastAPI · PyJWT · passlib/bcrypt · pytest
