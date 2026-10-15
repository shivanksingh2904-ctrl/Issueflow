import pytest

from issueflow.core.errors import ServiceUnavailableError
from issueflow.services.health import HealthService


class FakeRepo:
    def __init__(self, healthy: bool) -> None:
        self._healthy = healthy

    async def ping(self) -> bool:
        return self._healthy


async def test_ready_when_database_answers() -> None:
    await HealthService(FakeRepo(healthy=True)).check_ready()


async def test_raises_when_database_down() -> None:
    with pytest.raises(ServiceUnavailableError):
        await HealthService(FakeRepo(healthy=False)).check_ready()
