from __future__ import annotations

import json

from agentforecast.cli import main
from agentforecast.doctor import doctor
from agentforecast.mcp_server import dispatch_jsonrpc
from agentforecast.tool_server import dispatch_tool_call


_CORE_KEYS = {
    "installed_extras",
    "extra_status",
    "reviewed_backends",
    "reviewed_workflows_available",
    "missing_promoted_backends",
    "recommended_next_command",
    "links",
}


def _assert_doctor_shape(payload: dict) -> None:
    assert payload["kind"] == "agentforecast.doctor_report"
    assert _CORE_KEYS.issubset(payload.keys())
    assert "docs" in payload["links"]
    assert "paper_entry" in payload["links"]
    assert "mlforecast_linear" in payload["reviewed_backends"]
    assert "river_linear" in payload["reviewed_backends"]
    assert "river_snarimax" in payload["reviewed_backends"]


def test_doctor_python_api_has_expected_core_fields() -> None:
    payload = doctor()
    _assert_doctor_shape(payload)


def test_doctor_cli_tool_and_mcp_are_consistent(capsys) -> None:
    exit_code = main(["doctor", "--output", "json"])
    cli_payload = json.loads(capsys.readouterr().out)
    tool_payload = dispatch_tool_call("doctor", {})
    mcp_tool_payload = dispatch_jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "doctor", "arguments": {}},
        }
    )["result"]["result"]
    mcp_resource_payload = json.loads(
        dispatch_jsonrpc(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "resources/read",
                "params": {"uri": "package://agentforecast/doctor"},
            }
        )["result"]["contents"][0]["text"]
    )

    assert exit_code == 0
    _assert_doctor_shape(cli_payload)
    assert tool_payload["ok"] is True
    assert tool_payload["result"]["recommended_next_command"] == cli_payload["recommended_next_command"]
    assert tool_payload["result"]["reviewed_backends"] == cli_payload["reviewed_backends"]
    assert mcp_tool_payload["recommended_next_command"] == cli_payload["recommended_next_command"]
    assert mcp_tool_payload["reviewed_backends"] == cli_payload["reviewed_backends"]
    assert mcp_resource_payload["reviewed_backends"] == cli_payload["reviewed_backends"]
