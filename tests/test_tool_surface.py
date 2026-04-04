from __future__ import annotations

from agentforecast.tool_server import dispatch_tool_call


def test_tool_server_error_shape() -> None:
    payload = dispatch_tool_call("nope", {})
    assert payload["ok"] is False
    assert payload["error"]["code"] == "TOOL_NOT_FOUND"
    assert "schema_ref" in payload["error"]
    assert "retryable" in payload["error"]


def test_tool_server_lists_reviewed_backends() -> None:
    payload = dispatch_tool_call("list_reviewed_backends", {})
    backend_ids = {item["backend_id"] for item in payload["result"]}
    assert payload["ok"] is True
    assert "stats_ets" in backend_ids


def test_tool_server_backend_capabilities() -> None:
    payload = dispatch_tool_call("backend_capabilities", {"backend_id": "ml_ridge"})
    assert payload["ok"] is True
    assert payload["result"]["tier"] == "reviewed"
    assert payload["result"]["supports_exogenous"] is True
