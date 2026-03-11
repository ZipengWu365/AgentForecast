"""agentforecast: turn a time series into a publishable forecast pack."""

from .conformal import ConformalSpec
from .version import __version__
from .local import (
    shoot,
    snap,
    forecast_csv,
    forecast_url,
    forecast_dataset,
    forecast_dir,
    compare_backends,
    compare_backends_csv,
    compare_backends_dataset,
    forecast_stream_csv,
)
from .live import run_case, list_cases, get_case
from .datasets import list_datasets, get_dataset_spec, write_dataset
from .backends import list_backends, list_backend_families, route_backends
from .resources import describe_package
from .hosted import build_hosted_site


def vibe(*args, **kwargs):
    """Friendly alias of shoot() for vibe-coding flows."""
    return shoot(*args, **kwargs)


__all__ = [
    "__version__",
    "ConformalSpec",
    "shoot",
    "snap",
    "vibe",
    "forecast_csv",
    "forecast_url",
    "forecast_dataset",
    "forecast_dir",
    "compare_backends",
    "compare_backends_csv",
    "compare_backends_dataset",
    "forecast_stream_csv",
    "run_case",
    "list_cases",
    "get_case",
    "list_datasets",
    "get_dataset_spec",
    "write_dataset",
    "list_backends",
    "list_backend_families",
    "route_backends",
    "describe_package",
    "build_hosted_site",
]
