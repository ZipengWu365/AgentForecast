from __future__ import annotations

from typing import Any

from .backends import list_backend_capabilities
from .version import __version__


def diagnose_environment() -> dict[str, Any]:
    capabilities = list_backend_capabilities()
    available = [row for row in capabilities if row["available"]]
    unavailable = [row for row in capabilities if not row["available"]]
    profiles = {
        "pack": len([row for row in available if row["backend_id"] in {"naive", "ml_ridge", "stats_ets", "stream_ewm"}]) >= 2,
        "research": any(row["backend_id"] == "ml_ridge" for row in available),
        "streaming": any(row["backend_id"] in {"stream_ewm", "river_linear", "river_snarimax", "river_holtwinters"} for row in available),
        "agent": True,
        "full": len(unavailable) == 0,
    }
    recommended_commands = [
        "agentforecast forecast-csv path/to/data.csv --backend auto",
        "agentforecast benchmark-forecast path/to/data.csv --backend river_linear --horizons 1,3,6 --strict-mode",
        "agentforecast forecast-stream path/to/data.csv --backend stream_ewm",
    ]
    install_profiles = [
        {"profile": "base", "command": "pip install agentforecast", "best_for": "pack demos and lightweight one-shot forecasts"},
        {"profile": "research", "command": 'pip install "agentforecast[stats,ml]"', "best_for": "benchmarking and reproducible comparison work"},
        {"profile": "streaming", "command": 'pip install "agentforecast[stream]"', "best_for": "River-based streaming backends and online monitoring"},
        {"profile": "full", "command": 'pip install "agentforecast[all]"', "best_for": "broadest optional backend coverage"},
    ]
    return {
        "name": "agentforecast doctor",
        "tool_version": __version__,
        "profiles": profiles,
        "available_backend_count": len(available),
        "unavailable_backend_count": len(unavailable),
        "available_backends": [row["backend_id"] for row in available],
        "unavailable_backends": [
            {
                "backend_id": row["backend_id"],
                "reason": row["availability"]["reason"],
                "install_hint": row["availability"]["install_hint"],
            }
            for row in unavailable
        ],
        "install_profiles": install_profiles,
        "recommended_commands": recommended_commands,
        "backend_capabilities": capabilities,
    }


def doctor_report_text(payload: dict[str, Any]) -> str:
    lines = [
        f"agentforecast doctor {payload['tool_version']}",
        "",
        "Profiles:",
    ]
    for name, ok in payload["profiles"].items():
        lines.append(f"- {name}: {'yes' if ok else 'no'}")
    lines.extend(["", "Available backends:", "- " + ", ".join(payload["available_backends"]) if payload["available_backends"] else "- none"])
    if payload["unavailable_backends"]:
        lines.extend(["", "Unavailable backends:"])
        for item in payload["unavailable_backends"]:
            line = f"- {item['backend_id']}: {item['reason']}"
            if item["install_hint"]:
                line += f" | try `{item['install_hint']}`"
            lines.append(line)
    lines.extend(["", "Recommended commands:"] + [f"- {item}" for item in payload["recommended_commands"]])
    return "\n".join(lines)


__all__ = ["diagnose_environment", "doctor_report_text"]
