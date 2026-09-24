from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class DatabaseBaseSettings(BaseModel):
    driver: str
    user: str
    password: str
    host: str
    port: str
    db_name: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self):
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class DatabaseSettings(DatabaseBaseSettings):
    pass


class TestDatabaseSettings(DatabaseBaseSettings):
    pass


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certificates" / "private.pem"
    public_key_path: Path = BASE_DIR / "certificates" / "public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30


class SessionSettings(BaseModel):
    session_expire_seconds: int = 30 * 24 * 3600
    urlsafe_token_length: int = 32
    session_key: str = "cart_session_id"
    session_httponly: bool | None = None
    session_secure: bool | None = None
    same_site: str = "lax"


class ImageSettings(BaseModel):
    upload_dir: Path = "uploads"
    max_size: int = 10 * 1024 * 1024
    allowed_mime_types: list = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".webp"]


class LoggingSettings(BaseModel):
    log_dir: Path = BASE_DIR.parent / "uploads" / "logs"
    log_file_name: str = "app.log"
    log_level: str = "INFO"

    @property
    def log_file_path(self) -> Path:
        return self.log_dir / self.log_file_name


class CacheSettings(BaseModel):
    expire: int = 0


class SupabaseBucket(BaseModel):
    supabase_url: str
    supabase_key: str
    name: str


class S3Bucket(BaseModel):
    """Railway (or any S3-compatible) object storage credentials.

    All optional so the app still boots in supabase/local mode. Required
    only when STORAGE_BACKEND=s3. Values map to Railway's bucket
    variables:     endpoint          <- ENDPOINT           (e.g.
    https://t3.storageapi.dev)
    access_key_id     <- ACCESS_KEY_ID
    secret_access_key <- SECRET_ACCESS_KEY
    bucket            <- BUCKET             (unique S3 name, NOT display name)
    region            <- REGION             (e.g. "auto")

    """
    endpoint: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    bucket: Optional[str] = None
    region: str = "auto"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    environment: Literal["dev", "prod", "test"] = "dev"
    api_version_prefix: str = "/api/v1"
    database: DatabaseSettings
    allow_origins: str
    bucket: SupabaseBucket
    # Which storage backend to use: "supabase" (default), "s3" (Railway), or
    # "local" (disk). If unset, falls back to the environment-based default in
    # the DI container (local in dev, supabase in prod).
    storage_backend: Optional[Literal["supabase", "s3", "local"]] = None
    s3: S3Bucket = S3Bucket()
    auth_jwt: AuthJWT = AuthJWT()
    session: SessionSettings = SessionSettings()
    images: ImageSettings = ImageSettings()
    logging: LoggingSettings = LoggingSettings()
    cache: CacheSettings = CacheSettings()

    def model_post_init(self, __context: object) -> None:
        is_prod = self.environment == "prod"
        if self.session.session_secure is None:
            self.session.session_secure = is_prod
        if self.session.session_httponly is None:
            self.session.session_httponly = is_prod


settings = Settings()
