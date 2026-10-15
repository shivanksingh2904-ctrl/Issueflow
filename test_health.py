from typing import Any, Self

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.exc import OperationalError


class FakeSession:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.committed = False
        self.closed = False

    async def execute(self, statement: Any) -> None:
        if self.fail:
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    async def commit(self) -> None:
        self.committed = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        self.closed = True


def _use_session(app: FastAPI, session: FakeSession) -> None:
    app.state.session_factory = lambda: session


async def test_live(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_commits_and_closes_session(app: FastAPI, client: AsyncClient) -> None:
    session = FakeSession()
    _use_session(app, session)
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert session.committed
    assert session.closed


async def test_ready_returns_503_when_db_down(app: FastAPI, client: AsyncClient) -> None:
    session = FakeSession(fail=True)
    _use_session(app, session)
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"
    assert not session.committed
    assert session.closed


@pytest.mark.parametrize("path", ["/api/v1/docs", "/api/v1/redoc", "/api/v1/openapi.json"])
async def test_api_docs_enabled(client: AsyncClient, path: str) -> None:
    assert (await client.get(path)).status_code == 200


async def test_openapi_lists_health_routes(client: AsyncClient) -> None:
    paths = (await client.get("/api/v1/openapi.json")).json()["paths"]
    assert "/api/v1/health/live" in paths
    assert "/api/v1/health/ready" in paths
