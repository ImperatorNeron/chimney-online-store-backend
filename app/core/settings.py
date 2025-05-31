from pathlib import Path

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
    session_httponly: bool = True
    session_secure: bool = True  # Change
    same_site: str = "None"  # Change


class ImageSettings(BaseModel):
    upload_dir: Path = BASE_DIR / "images"
    max_size: int = 10 * 1024 * 1024
    allowed_mime_types: list = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".webp"]


class LoggingSettings(BaseModel):
    log_dir: Path = BASE_DIR / "logs"
    log_file_name: str = "app.log"
    log_level: str = "INFO"

    @property
    def log_file_path(self) -> Path:
        return self.log_dir / self.log_file_name


class CacheSettings(BaseModel):
    expire: int = 600


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    api_version_prefix: str = "/api/v1"
    database: DatabaseSettings
    allow_origins: str
    auth_jwt: AuthJWT = AuthJWT()
    session: SessionSettings = SessionSettings()
    images: ImageSettings = ImageSettings()
    logging: LoggingSettings = LoggingSettings()
    cache: CacheSettings = CacheSettings()


settings = Settings()
