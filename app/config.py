import os


class Settings:
    """Konfigurasjon for applikasjonen.

    I produksjon må SECRET_KEY komme fra miljøet (eller et hemmelighetshvelv
    som Azure Key Vault) og aldri sjekkes inn i kildekoden.
    """

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


settings = Settings()
