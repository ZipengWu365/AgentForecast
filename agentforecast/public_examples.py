from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PublicExampleSpec:
    data_id: str
    file_name: str
    title: str
    description: str
    provenance: str
    source_url: str
    date_col: str = "ds"
    value_col: str = "y"
    series_kind: str = "auto"
    default_horizon: int = 12

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_id": self.data_id,
            "file_name": self.file_name,
            "title": self.title,
            "description": self.description,
            "provenance": self.provenance,
            "source_url": self.source_url,
            "date_col": self.date_col,
            "value_col": self.value_col,
            "series_kind": self.series_kind,
            "default_horizon": self.default_horizon,
        }


_PUBLIC_EXAMPLES = (
    PublicExampleSpec(
        data_id="monthly-car-sales",
        file_name="monthly_car_sales.csv",
        title="Monthly car sales",
        description="Real monthly car sales with strong seasonal structure that makes forecast quality visible at a glance.",
        provenance="Public historical series mirrored by Jason Brownlee's Datasets repository.",
        source_url="https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv",
        default_horizon=12,
    ),
    PublicExampleSpec(
        data_id="airline-passengers",
        file_name="airline_passengers.csv",
        title="Airline passengers",
        description="Real monthly airline passenger counts used widely in forecasting benchmarks because the seasonal growth pattern is easy to interpret.",
        provenance="Public historical airline passenger series mirrored by Jason Brownlee's Datasets repository.",
        source_url="https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv",
        default_horizon=12,
    ),
    PublicExampleSpec(
        data_id="daily-min-temperatures",
        file_name="daily_min_temperatures.csv",
        title="Daily minimum temperatures",
        description="Real daily temperature observations with strong seasonal memory, suitable for lag-feature regression and streaming examples.",
        provenance="Public historical temperature series mirrored by Jason Brownlee's Datasets repository.",
        source_url="https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv",
        default_horizon=30,
    ),
)


def list_public_example_specs() -> list[dict[str, Any]]:
    return [spec.to_dict() for spec in _PUBLIC_EXAMPLES]


def get_public_example_spec(data_id: str) -> PublicExampleSpec:
    for spec in _PUBLIC_EXAMPLES:
        if spec.data_id == data_id:
            return spec
    raise ValueError(f"Unknown public example dataset '{data_id}'.")


def public_example_path(data_id: str) -> Path:
    spec = get_public_example_spec(data_id)
    return Path(resources.files("agentforecast.package_data.public_examples").joinpath(spec.file_name))
