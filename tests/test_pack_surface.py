from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from agentforecast import forecast_csv, forecast_dataset, shoot
from agentforecast.public_examples import public_example_path


def test_forecast_dataset_creates_manifest_and_resolution(tmp_path: Path) -> None:
    result = forecast_dataset("sales", outdir=tmp_path)
    payload = result.to_dict()
    root = tmp_path / "sales"
    manifest = json.loads((root / "meta" / "artifact_manifest.json").read_text(encoding="utf-8"))

    assert payload["resolution"]["resolved_backend"] == payload["backend_selected"]
    assert manifest["backend_selected"] == payload["backend_selected"]
    assert manifest["artifact_count"] == len(payload["artifacts"])
    assert any(item["kind"] == "artifact_manifest_json" for item in payload["artifacts"])


def test_forecast_csv_keeps_monthly_future_dates(tmp_path: Path) -> None:
    result = forecast_csv(public_example_path("monthly-car-sales"), backend="naive", outdir=tmp_path, horizon=3)
    forecast = pd.read_csv(next(tmp_path.glob("*/data/forecast.csv")))

    assert result.inputs["name"] == "monthly_car_sales"
    assert forecast["ds"].tolist() == ["1969-01-01", "1969-02-01", "1969-03-01"]


def test_shoot_routes_dataset_ids(tmp_path: Path) -> None:
    result = shoot("sales", outdir=tmp_path)
    assert result.summary["headline"]
    assert (tmp_path / "sales" / "meta" / "metadata.json").exists()
