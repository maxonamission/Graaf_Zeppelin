from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Graaf Zeppelin"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "sqlite+aiosqlite:///./graaf_zeppelin.db"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    dag_models_path: str = "data/models"
    graph_model_path: str = "data/models/sportdeelname_graph.json"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
