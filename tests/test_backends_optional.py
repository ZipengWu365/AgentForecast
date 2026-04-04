from __future__ import annotations

from pathlib import Path

import pytest

from agentforecast import forecast_dataset, list_backends
from agentforecast.backends import is_backend_available


@pytest.mark.optional
def test_optional_registry_marks_experimental_and_planned_surfaces() -> None:
    registry = {item["backend_id"]: item["tier"] for item in list_backends(include_unavailable=True)}
    assert registry["statsforecast_autoarima"] == "experimental"
    assert registry["neural_nhits"] == "planned"


@pytest.mark.optional
def test_optional_backend_smoke_when_any_optional_backend_is_installed(tmp_path: Path) -> None:
    backend = next(
        (
            backend_id
            for backend_id in ["statsforecast_autoarima", "mlforecast_linear", "river_linear"]
            if is_backend_available(backend_id)
        ),
        None,
    )
    if backend is None:
        pytest.skip("no optional backend extra is installed in this environment")

    result = forecast_dataset("sales", backend=backend, outdir=tmp_path, strict_backend=True, mode="benchmark")
    assert result.backend_selected == backend
