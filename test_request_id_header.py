from httpx import AsyncClient


async def test_generates_request_id(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")
    assert len(response.headers["X-Request-ID"]) == 32


async def test_echoes_valid_request_id(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live", headers={"X-Request-ID": "trace-42"})
    assert response.headers["X-Request-ID"] == "trace-42"


async def test_replaces_invalid_request_id(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live", headers={"X-Request-ID": "bad id!"})
    assert response.headers["X-Request-ID"] != "bad id!"
