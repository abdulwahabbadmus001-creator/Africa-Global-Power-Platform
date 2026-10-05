from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Africa & Global Power API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    secret_key: str = "change-me"
    access_token_minutes: int = 480
    database_url: str = "postgresql+psycopg://agp:agp_local_password@localhost:5434/agp"
    cors_origins: str = "http://localhost:5173"
    cookie_secure: bool = False
    cookie_domain: str | None = None
    public_site_url: str = "http://localhost:5173"
    contact_recipient_email: str = ""

    otp_length: int = 8
    otp_expiry_minutes: int = 10
    otp_resend_seconds: int = 60
    otp_max_attempts: int = 5

    editor_session_minutes: int = 60
    editorial_challenge_minutes: int = 10
    mfa_secret_key: str = "change-this-mfa-secret"
    mfa_issuer: str = "Africa & Global Power"
    recovery_code_count: int = 10

    trust_log_secret: str = "change-this-trust-log-secret"
    trust_statement_version: str = "2026-10-05"
    max_manuscript_mb: int = 25

    storage_backend: str = "local"
    storage_local_path: str = "private_uploads"
    storage_s3_endpoint_url: str = ""
    storage_s3_region: str = "us-east-1"
    storage_s3_bucket: str = ""
    storage_s3_access_key_id: str = ""
    storage_s3_secret_access_key: str = ""
    storage_s3_force_path_style: bool = True

    email_delivery_mode: str = "console"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = ""
    email_from_name: str = "Africa & Global Power"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
