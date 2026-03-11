from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AgentForecastError(Exception):
    code: str
    message: str
    help_text: str | None = None
    details: dict[str, Any] | None = None
    retryable: bool = False

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "kind": "agentforecast.error",
            "schema_version": "1.1.0",
            "schema_ref": "package://agentforecast/package_data/schemas/error.schema.json",
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.help_text:
            payload["help"] = self.help_text
        if self.details:
            payload["details"] = self.details
        return payload


def ensure(condition: bool, code: str, message: str, *, help_text: str | None = None, details: dict[str, Any] | None = None, retryable: bool = False) -> None:
    if not condition:
        raise AgentForecastError(code=code, message=message, help_text=help_text, details=details, retryable=retryable)
