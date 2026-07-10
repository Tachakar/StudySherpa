from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    postgres_test_port: int
    qdrant_port: int

    jwt_secret_key: str
    jwt_expires_minutes: int
    jwt_algorithm: str
    refresh_token_expires_days: int

    login_rate_limit: str
    register_rate_limit: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_port}/{self.postgres_db}"

    @property
    def test_database_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_test_port}/test_db"


settings = Settings()
