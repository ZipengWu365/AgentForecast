from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentforecast import forecast_stream_csv
from agentforecast.backends import is_backend_available
from agentforecast.public_examples import public_example_path


def _load_manifest(run_root: Path) -> dict:
    manifest_path = next(run_root.rglob("artifact_manifest.json"))
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@pytest.mark.optional
@pytest.mark.parametrize("backend_id", ["river_linear", "river_snarimax"])
def test_reviewed_river_backends_generate_streaming_pack(tmp_path: Path, backend_id: str) -> None:
    if not is_backend_available(backend_id):
        pytest.skip(f"{backend_id} is not installed in this environment")

    result = forecast_stream_csv(
        public_example_path("daily-min-temperatures"),
        backend=backend_id,
        horizon=7,
        outdir=tmp_path,
        strict_backend=True,
    )
    manifest = _load_manifest(tmp_path)

    assert result.backend_selected == backend_id
    assert result.resolution.resolved_backend == backend_id
    assert result.diagnostics["streaming"]["backend_family"] == "streaming"
    assert manifest["backend_selected"] == backend_id
    assert manifest["resolution"]["requested_backend"] == backend_id
    assert manifest["resolution"]["resolved_backend"] == backend_id
