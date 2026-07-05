from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int
    qdrant_port: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
