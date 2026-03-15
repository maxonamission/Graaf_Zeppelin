import logging
import warnings

from pydantic_settings import BaseSettings

_logger = logging.getLogger(__name__)

_INSECURE_DEFAULTS = frozenset({
    "dev-secret-key-change-in-production",
    "secret",
    "changeme",
})


class Settings(BaseSettings):
    app_name: str = "Graaf Zeppelin"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    # SQLite for development, PostgreSQL for production
    # Set DATABASE_URL=postgresql+asyncpg://user:pass@host/db for production
    database_url: str = "sqlite+aiosqlite:///./graaf_zeppelin.db"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    dag_models_path: str = "data/models"
    graph_model_path: str = "data/models/sportdeelname_graph.json"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    def validate_secret_key(self) -> None:
        """Validate that the secret key is safe for the current environment."""
        is_weak = (
            self.secret_key in _INSECURE_DEFAULTS
            or len(self.secret_key) < 32
            or "change-in-production" in self.secret_key
        )
        if self.environment == "production" and is_weak:
            raise ValueError(
                "FATAL: SECRET_KEY is onveilig voor productie. "
                "Stel een willekeurige sleutel in van minimaal 32 tekens via de "
                "SECRET_KEY omgevingsvariabele."
            )
        if is_weak:
            warnings.warn(
                "SECRET_KEY gebruikt een onveilige standaardwaarde. "
                "Stel een sterke sleutel in via de SECRET_KEY omgevingsvariabele.",
                stacklevel=2,
            )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
settings.validate_secret_key()
