from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentforecast.backends import is_backend_available
from agentforecast.errors import AgentForecastError
from agentforecast.streaming_eval import stream_eval
from agentforecast.types import STREAMING_EVAL_SCHEMA_REF


def test_streaming_pilot_strict_mode_rejects_missing_backend(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import agentforecast.streaming_eval as streaming_eval_module

    monkeypatch.setattr(
        streaming_eval_module,
        "is_backend_available",
        lambda backend_id: False if backend_id == "river_linear" else is_backend_available(backend_id),
    )

    with pytest.raises(AgentForecastError) as exc:
        stream_eval(outdir=tmp_path, backends=["river_linear"], strict_backend=True)

    assert exc.value.code == "BACKEND_UNAVAILABLE"


@pytest.mark.optional
def test_streaming_pilot_generates_annex_artifacts(tmp_path: Path) -> None:
    required = ["stream_ewm", "river_linear", "river_snarimax"]
    missing = [backend_id for backend_id in required if not is_backend_available(backend_id)]
    if missing:
        pytest.skip(f"streaming pilot backends not installed: {', '.join(missing)}")

    payload = stream_eval(outdir=tmp_path, backends=required, warmup=24, strict_backend=True)
    root = tmp_path / "streaming-eval"
    manifest = json.loads((root / "meta" / "streaming_eval_manifest.json").read_text(encoding="utf-8"))

    assert payload.schema_ref == STREAMING_EVAL_SCHEMA_REF
    assert (root / "metrics" / "prequential_metrics.csv").exists()
    assert (root / "metrics" / "system_metrics.json").exists()
    assert (root / "plots" / "prequential_error.png").exists()
    assert (root / "reports" / "summary.md").exists()
    assert manifest["kind"] == "agentforecast.streaming_eval_manifest"
    assert manifest["schema_ref"] == STREAMING_EVAL_SCHEMA_REF
    assert "daily-min-temperatures" in payload.inputs["datasets"]
    assert "river-flood-risk" in payload.inputs["datasets"]
    assert {row["backend_id"] for row in payload.metrics} >= {"stream_ewm", "river_linear", "river_snarimax"}
