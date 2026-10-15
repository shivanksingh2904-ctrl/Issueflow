import pytest

from issueflow.core.middleware import resolve_request_id


def test_keeps_valid_client_id() -> None:
    assert resolve_request_id("abc-123_X.9") == "abc-123_X.9"


@pytest.mark.parametrize("bad", [None, "", "has space", "x" * 65, "new\nline", "<script>"])
def test_replaces_missing_or_malformed_id(bad: str | None) -> None:
    generated = resolve_request_id(bad)
    assert generated != bad
    assert len(generated) == 32
