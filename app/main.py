from fastapi import FastAPI

from app.routers import auth_router, users_router

app = FastAPI(
    title="IAM REST API",
    description="A secure REST API demonstrating JWT authentication and "
    "role-based access control (RBAC).",
    version="1.0.0",
)

app.include_router(auth_router.router)
app.include_router(users_router.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "iam-rest-api"}
