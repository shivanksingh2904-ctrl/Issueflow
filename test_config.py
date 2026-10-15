import pytest
from pydantic import ValidationError

from issueflow.core.config import Settings, get_settings


def test_defaults() -> None:
    settings = Settings(_env_file=None)
    assert settings.environment == "local"
    assert settings.log_level == "INFO"
    assert settings.database_url.startswith("postgresql+asyncpg://")


def test_reads_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/x")
    settings = Settings(_env_file=None)
    assert settings.environment == "production"
    assert settings.log_level == "ERROR"
    assert settings.database_url == "postgresql+asyncpg://u:p@db:5432/x"


def test_rejects_sync_driver_url() -> None:
    with pytest.raises(ValidationError, match="async driver"):
        Settings(database_url="postgresql://u:p@db/x", _env_file=None)


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()
