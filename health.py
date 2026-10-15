from typing import Protocol

from issueflow.core.errors import ServiceUnavailableError


class SupportsPing(Protocol):
    async def ping(self) -> bool: ...


class HealthService:
    def __init__(self, repository: SupportsPing) -> None:
        self._repository = repository

    async def check_ready(self) -> None:
        if not await self._repository.ping():
            raise ServiceUnavailableError("Database is unavailable")
