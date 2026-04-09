from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentforecast import forecast_csv, forecast_dataset
from agentforecast.backends import is_backend_available
from agentforecast.public_examples import public_example_path


def _load_manifest(run_root: Path) -> dict:
    manifest_path = next(run_root.rglob("artifact_manifest.json"))
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@pytest.mark.optional
@pytest.mark.parametrize("example_id", ["monthly-car-sales", "airline-passengers"])
def test_reviewed_mlforecast_linear_generates_e2e_pack(tmp_path: Path, example_id: str) -> None:
    if not is_backend_available("mlforecast_linear"):
        pytest.skip("mlforecast_linear is not installed in this environment")

    result = forecast_csv(
        public_example_path(example_id),
        backend="mlforecast_linear",
        horizon=12,
        outdir=tmp_path,
        strict_backend=True,
        mode="benchmark",
    )
    manifest = _load_manifest(tmp_path)

    assert result.backend_selected == "mlforecast_linear"
    assert result.resolution.resolved_backend == "mlforecast_linear"
    assert manifest["backend_selected"] == "mlforecast_linear"
    assert manifest["resolution"]["requested_backend"] == "mlforecast_linear"
    assert manifest["resolution"]["resolved_backend"] == "mlforecast_linear"


@pytest.mark.optional
def test_reviewed_mlforecast_linear_handles_exogenous_contract(tmp_path: Path) -> None:
    if not is_backend_available("mlforecast_linear"):
        pytest.skip("mlforecast_linear is not installed in this environment")

    result = forecast_dataset(
        "gold-exogenous",
        backend="mlforecast_linear",
        outdir=tmp_path,
        strict_backend=True,
        mode="benchmark",
    )
    manifest = _load_manifest(tmp_path)

    assert result.backend_selected == "mlforecast_linear"
    assert result.inputs["dataset_id"] == "gold-exogenous"
    assert manifest["resolution"]["requested_backend"] == "mlforecast_linear"
    assert manifest["resolution"]["resolved_backend"] == "mlforecast_linear"
