"""agentforecast: publishable forecast packs plus benchmark-friendly forecasting APIs."""

from .conformal import ConformalSpec
from .features import FeatureSpec, list_feature_presets
from .version import __version__
from .local import (
    shoot,
    snap,
    forecast_dataframe,
    forecast_csv,
    forecast_url,
    forecast_dataset,
    forecast_dir,
    compare_backends_frame,
    compare_backends,
    compare_backends_csv,
    compare_backends_dataset,
    forecast_stream_dataframe,
    forecast_stream_csv,
)
from .benchmark import BenchmarkForecastResult, OnlineForecaster, forecast_benchmark_dataframe
from .live import run_case, list_cases, get_case
from .datasets import list_datasets, get_dataset_spec, write_dataset
from .backends import list_backends, list_backend_families, route_backends, supports_direct_forecast
from .resources import describe_package
from .examples_hub import build_examples_site, demo_examples, list_examples
from .hosted import build_hosted_site


def vibe(*args, **kwargs):
    """Friendly alias of shoot() for vibe-coding flows."""
    return shoot(*args, **kwargs)


__all__ = [
    "__version__",
    "ConformalSpec",
    "FeatureSpec",
    "BenchmarkForecastResult",
    "OnlineForecaster",
    "shoot",
    "snap",
    "vibe",
    "forecast_benchmark_dataframe",
    "forecast_dataframe",
    "forecast_csv",
    "forecast_url",
    "forecast_dataset",
    "forecast_dir",
    "compare_backends_frame",
    "compare_backends",
    "compare_backends_csv",
    "compare_backends_dataset",
    "forecast_stream_dataframe",
    "forecast_stream_csv",
    "run_case",
    "list_cases",
    "get_case",
    "list_datasets",
    "get_dataset_spec",
    "write_dataset",
    "list_backends",
    "list_backend_families",
    "list_feature_presets",
    "route_backends",
    "supports_direct_forecast",
    "describe_package",
    "list_examples",
    "demo_examples",
    "build_examples_site",
    "build_hosted_site",
]
