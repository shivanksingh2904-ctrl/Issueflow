from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class HealthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def ping(self) -> bool:
        """Return True if the database answers a trivial query."""
        try:
            await self._session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return False
        return True
