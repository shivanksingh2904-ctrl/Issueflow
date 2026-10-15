import json
import logging
import sys

import pytest

from issueflow.core.logging import JsonFormatter, configure_logging, request_id_ctx


def _record(message: str = "hello", **extra: object) -> logging.LogRecord:
    record = logging.LogRecord("t", logging.INFO, __file__, 1, message, (), None)
    record.__dict__.update(extra)
    return record


def test_formatter_emits_json_with_request_id_and_extras() -> None:
    token = request_id_ctx.set("req-1")
    try:
        payload = json.loads(JsonFormatter().format(_record(status_code=200)))
    finally:
        request_id_ctx.reset(token)
    assert payload["message"] == "hello"
    assert payload["level"] == "INFO"
    assert payload["request_id"] == "req-1"
    assert payload["status_code"] == 200


def test_formatter_includes_exception() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord("t", logging.ERROR, __file__, 1, "x", (), sys.exc_info())
    assert "ValueError: boom" in json.loads(JsonFormatter().format(record))["exception"]


def test_configure_logging_is_idempotent(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")
    configure_logging("INFO")
    logging.getLogger("issueflow.test").info("once")
    lines = [line for line in capsys.readouterr().out.splitlines() if "once" in line]
    assert len(lines) == 1
    assert json.loads(lines[0])["message"] == "once"
