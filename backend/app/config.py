"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings."""

    # Time acceleration: 1 real second = N simulation minutes
    time_acceleration: int = 60

    # Database
    database_url: str = "sqlite:///./flight_simulator.db"

    # Metric recording interval (seconds of real time)
    metric_interval_seconds: int = 10

    # Enable background metric recorder (disable in tests)
    recorder_enabled: bool = True

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")


settings = Settings()
