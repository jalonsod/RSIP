from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "RSIP API"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://rsip:rsip@localhost:5432/rsip"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # External APIs
    zillow_api_key: str = ""
    realtor_api_key: str = ""
    lms_api_url: str = ""
    lms_api_key: str = ""
    crexy_api_key: str = ""

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
