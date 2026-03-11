from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any
from .version import __version__


@dataclass
class ArtifactRef:
    kind: str
    path: str
    media_type: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunResult:
    run_type: str
    backend_selected: str
    candidate_backends: list[str]
    feature_spec: dict[str, Any]
    inputs: dict[str, Any]
    summary: dict[str, Any]
    diagnostics: dict[str, Any]
    metrics: dict[str, Any]
    artifacts: list[ArtifactRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    used_live_data: bool = False
    kind: str = "agentforecast.run_result"
    schema_version: str = "1.0.0"
    schema_ref: str = "package://agentforecast/package_data/schemas/run_result.schema.json"
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass
class CompareResult:
    run_type: str
    backend_selected: str
    candidate_backends: list[str]
    feature_spec: dict[str, Any]
    inputs: dict[str, Any]
    summary: dict[str, Any]
    diagnostics: dict[str, Any]
    metrics: dict[str, Any]
    leaderboard: list[dict[str, Any]]
    artifacts: list[ArtifactRef] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    used_live_data: bool = False
    kind: str = "agentforecast.compare_result"
    schema_version: str = "1.0.0"
    schema_ref: str = "package://agentforecast/package_data/schemas/compare_result.schema.json"
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass
class DirectoryRunResult:
    inputs: dict[str, Any]
    runs: list[RunResult]
    warnings: list[str] = field(default_factory=list)
    kind: str = "agentforecast.directory_run_result"
    schema_version: str = "1.0.0"
    schema_ref: str = "package://agentforecast/package_data/schemas/directory_run_result.schema.json"
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "schema_version": self.schema_version,
            "schema_ref": self.schema_ref,
            "tool_version": self.tool_version,
            "inputs": self.inputs,
            "runs": [run.to_dict() for run in self.runs],
            "warnings": self.warnings,
        }
