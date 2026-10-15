from typing import Annotated

from fastapi import APIRouter, Depends

from issueflow.api.v1.deps import get_health_service
from issueflow.core.errors import ErrorResponse
from issueflow.schemas.health import HealthResponse
from issueflow.services.health import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness probe")
async def live() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    summary="Readiness probe (checks the database)",
    responses={503: {"model": ErrorResponse, "description": "Database unavailable"}},
)
async def ready(service: Annotated[HealthService, Depends(get_health_service)]) -> HealthResponse:
    await service.check_ready()
    return HealthResponse(status="ok")
