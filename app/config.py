import os


class Settings:
    """Application configuration.

    In production, SECRET_KEY must come from the environment (or a secrets
    manager / Azure Key Vault) and never be committed to source control.
    """

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()
