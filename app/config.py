import secrets
from typing import Any, Dict, List, Optional, Union, Tuple
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class PostgresSettings(BaseSettings):
    DB_HOST: str = "memoires-db"
    DB_USER: str = "memoires"
    DB_PASSWORD: str = "memoires"
    DB_PORT: str = "5432"
    DB_NAME: str = "memoires"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> PostgresDsn:

        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}",
        )


class MinioSettings(BaseSettings):
    MINIO_ADDR: str = "memoires-minio"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "memoires"
    MINIO_ACCESS_PASSWORD: str = "memoires"
    MINIO_SSL: bool = False
    MINIO_BUCKET: str = "memoires"


class ApplicationSettings(BaseSettings):
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Memoires"

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:4200",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    MAX_THUMBNAIL_SIZE: Tuple[int, int] = (800, 800)

    class Config:
        case_sensitive = True


class Settings(PostgresSettings, ApplicationSettings, MinioSettings):
    pass


settings = Settings()
