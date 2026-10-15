from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from issueflow.repositories.health import HealthRepository
from issueflow.services.health import HealthService


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    """One transaction per request: commit on success, roll back if anything raises."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        yield session
        await session.commit()


DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_health_service(session: DbSession) -> HealthService:
    return HealthService(HealthRepository(session))
