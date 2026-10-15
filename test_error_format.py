from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from issueflow.core.errors import AppError


class Payload(BaseModel):
    name: str


class TeapotError(AppError):
    status_code = 418
    code = "teapot"


async def _validate(payload: Payload) -> Payload:
    return payload


async def _raise_app_error() -> None:
    raise TeapotError("short and stout", details=[{"field": "spout"}])


async def _raise_unhandled() -> None:
    raise RuntimeError("secret internal detail")


def _add_routes(app: FastAPI) -> None:
    app.add_api_route("/_t/validate", _validate, methods=["POST"])
    app.add_api_route("/_t/app-error", _raise_app_error, methods=["GET"])
    app.add_api_route("/_t/unhandled", _raise_unhandled, methods=["GET"])


async def test_unknown_route_uses_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/nope")
    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Not Found", "details": []}}


async def test_method_not_allowed_uses_error_envelope(client: AsyncClient) -> None:
    response = await client.post("/api/v1/health/live")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "method_not_allowed"


async def test_validation_error_lists_fields(app: FastAPI, client: AsyncClient) -> None:
    _add_routes(app)
    response = await client.post("/_t/validate", json={})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["loc"] == ["body", "name"]


async def test_app_error_is_rendered(app: FastAPI, client: AsyncClient) -> None:
    _add_routes(app)
    response = await client.get("/_t/app-error")
    assert response.status_code == 418
    assert response.json() == {
        "error": {"code": "teapot", "message": "short and stout", "details": [{"field": "spout"}]}
    }


async def test_unhandled_error_is_generic_and_keeps_request_id(app: FastAPI) -> None:
    _add_routes(app)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        response = await http.get("/_t/unhandled", headers={"X-Request-ID": "rid-500"})
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "secret" not in response.text
    assert response.headers["X-Request-ID"] == "rid-500"
