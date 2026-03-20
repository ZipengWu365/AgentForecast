from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import numpy as np

import agentforecast
from agentforecast import ConformalSpec, FeatureSpec, forecast_dataset, forecast_stream_dataframe, shoot
from agentforecast.backends import is_backend_available, list_backends, route_backends
from agentforecast.doctor import diagnose_environment
from agentforecast.datasets import dataset_path, get_dataset_spec
from agentforecast.examples_hub import build_examples_site, demo_examples, list_examples
from agentforecast.local import compare_backends_csv
from agentforecast.features import build_feature_spec, clean_series_frame, prepare_series_frame, validate_series_frame
from agentforecast.errors import AgentForecastError
from agentforecast.hosted import build_hosted_site
from agentforecast.local import compare_backends_dataset, forecast_csv, forecast_stream_csv
from agentforecast.mcp_server import dispatch_jsonrpc
from agentforecast.public_examples import public_example_path
from agentforecast.tool_server import dispatch_tool_call

TSFRESH_AVAILABLE = importlib.util.find_spec("tsfresh") is not None
SKLEARN_AVAILABLE = importlib.util.find_spec("sklearn") is not None
ONLINE_FORECASTER_AVAILABLE = hasattr(agentforecast, "OnlineForecaster")


class AgentForecastV17Tests(unittest.TestCase):
    def _monthly_history(self, n: int = 72) -> pd.DataFrame:
        return pd.read_csv(public_example_path("monthly-car-sales")).tail(n).reset_index(drop=True)

    def _assert_requested_horizons(self, forecast: object, expected: set[int] | None = None) -> None:
        expected = expected or {1, 3, 6}
        if isinstance(forecast, dict):
            self.assertEqual({int(key) for key in forecast.keys()}, expected)
            return
        if isinstance(forecast, pd.DataFrame):
            columns = {str(col) for col in forecast.columns}
            if "horizon" in columns:
                self.assertEqual({int(value) for value in forecast["horizon"].tolist()}, expected)
                return
            direct_cols = {int(col[1:]) for col in columns if col.startswith("h") and col[1:].isdigit()}
            if direct_cols:
                self.assertEqual(direct_cols, expected)
                return
            if {str(value) for value in expected}.issubset(columns):
                return
        if isinstance(forecast, np.ndarray):
            self.assertGreaterEqual(forecast.size, len(expected))
            if forecast.ndim > 0 and forecast.shape[-1] == len(expected):
                return
        if isinstance(forecast, (list, tuple)) and len(forecast) == len(expected):
            return
        self.fail(f"Unexpected multi-horizon forecast payload: {type(forecast)!r}")

    def test_forecast_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset('sales', outdir=tmp)
            self.assertIn('headline', result.summary)
            self.assertEqual(result.inputs['dataset_id'], 'sales')
            self.assertTrue((Path(tmp) / 'sales' / 'meta' / 'metadata.json').exists())

    def test_compare_backends_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = compare_backends_dataset('gold', backends=['naive', 'moving_average', 'stats_arima'], outdir=tmp)
            self.assertGreaterEqual(len(result.leaderboard), 2)
            self.assertIn(result.backend_selected, [row['backend_id'] for row in result.leaderboard])

    def test_route_backends(self) -> None:
        route = route_backends(history_len=50, horizon=14, strategy='streaming', exogenous_cols=[])
        self.assertIn('candidate_backends', route)
        self.assertIn('stream_ewm', route['candidate_backends'])

    def test_list_backends_contains_new_entries(self) -> None:
        backend_ids = {row['backend_id'] for row in list_backends()}
        self.assertIn('stream_ewm', backend_ids)
        self.assertIn('statsforecast_autoarima', backend_ids)
        self.assertIn('mlforecast_linear', backend_ids)

    def test_forecast_stream_builtin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_stream_csv(dataset_path('icu-bed-stress'), backend='stream_ewm', outdir=tmp)
            self.assertEqual(result.backend_selected, 'stream_ewm')
            self.assertIn('streaming', result.diagnostics)

    def test_forecast_stream_dataframe(self) -> None:
        frame = pd.read_csv(public_example_path('daily-min-temperatures')).tail(180)
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_stream_dataframe(frame, name='daily_min_temperatures', backend='stream_ewm', outdir=tmp, horizon=7)
            self.assertEqual(result.run_type, 'forecast_stream_dataframe')
            self.assertIn('streaming', result.diagnostics)

    def test_tool_server_error_shape(self) -> None:
        payload = dispatch_tool_call('nope', {})
        self.assertFalse(payload['ok'])
        self.assertEqual(payload['error']['code'], 'TOOL_NOT_FOUND')
        self.assertIn('schema_ref', payload['error'])
        self.assertIn('retryable', payload['error'])

    def test_mcp_resources(self) -> None:
        response = dispatch_jsonrpc({'jsonrpc': '2.0', 'id': 1, 'method': 'resources/list'})
        self.assertIn('result', response)
        resources = response['result']['resources']
        self.assertTrue(any(item['uri'] == 'package://agentforecast/overview' for item in resources))

    def test_build_hosted_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / 'runs'
            site = Path(tmp) / 'site'
            shoot('sales', outdir=runs)
            manifest = build_hosted_site(runs, site)
            self.assertEqual(manifest['entry_count'], 1)
            self.assertTrue((site / 'index.html').exists())
            feed = json.loads((site / 'feed.json').read_text(encoding='utf-8'))
            self.assertEqual(len(feed['items']), 1)
            index_text = (site / 'index.html').read_text(encoding='utf-8')
            self.assertIn('Real forecasting models, not toy demos', index_text)
            self.assertIn('What the package actually includes', index_text)
            self.assertIn('stats_ets, stats_arima, statsforecast_autoets, statsforecast_autoarima', index_text)
            self.assertIn('One package, four explicit surfaces', index_text)
            self.assertIn('Choose a calm first path', index_text)
            self.assertIn('Backend capability matrix', index_text)
            self.assertIn('Backend families and model ids', index_text)
            self.assertIn('Python API surface', index_text)
            self.assertIn('OnlineForecaster', index_text)
            self.assertIn('diagnose_environment', index_text)
            self.assertIn('Package capabilities', index_text)

    def test_summary_markdown_is_generated_without_tabulate_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset('sales', outdir=tmp)
            summary_path = Path(tmp) / 'sales' / 'reports' / 'summary.md'
            text = summary_path.read_text(encoding='utf-8')
            self.assertIn('| backend_id |', text)
            self.assertEqual(result.backend_selected in text, True)

    def test_river_linear_conformal_emits_interval_metrics(self) -> None:
        if not is_backend_available('river_linear'):
            self.skipTest('river extra is not installed')
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset(
                'sales',
                backend='river_linear',
                outdir=tmp,
                conformal=ConformalSpec(enabled=True, levels=(80, 90, 95), calibration_window=50, warmup_min=5),
            )
            conformal = result.diagnostics['conformal']
            self.assertEqual(conformal['method'], 'river_jackknife')
            self.assertIn('90', conformal['coverage_backtest'])
            self.assertIn('90', conformal['mean_interval_width'])
            forecast_path = Path(tmp) / 'sales' / 'data' / 'forecast.csv'
            forecast_text = forecast_path.read_text(encoding='utf-8')
            self.assertIn('lower_95', forecast_text)
            self.assertIn('upper_95', forecast_text)
            self.assertIn('coverage_90', result.metrics)
            self.assertIn('avg_width_90', result.metrics)

    def test_build_feature_spec_supports_custom_lag_and_delay_features(self) -> None:
        frame = pd.read_csv(dataset_path('gold-exogenous'))
        prepared = prepare_series_frame(frame)
        spec = build_feature_spec(
            prepared.history,
            feature_spec=FeatureSpec(
                lag_points=(1, 5, 9),
                lag_step=7,
                lag_count=4,
                rolling_windows=(3, 8, 21),
                include_tsfresh=TSFRESH_AVAILABLE,
                tsfresh_window=21,
            ),
        )
        self.assertEqual(spec['lags'], [1, 5, 7, 9, 14, 21, 28])
        self.assertEqual(spec['rolling_windows'], [3, 8, 21])
        self.assertEqual(spec['lag_step'], 7)
        self.assertEqual(spec['lag_count'], 4)
        self.assertEqual(spec['include_tsfresh'], TSFRESH_AVAILABLE)
        if TSFRESH_AVAILABLE:
            self.assertIn('sample_entropy', spec['tsfresh_features'])

    def test_online_forecaster_is_public_and_supports_recursive_multi_horizon(self) -> None:
        self.assertTrue(ONLINE_FORECASTER_AVAILABLE, "agentforecast.OnlineForecaster is not exported.")
        self.assertIn("OnlineForecaster", getattr(agentforecast, "__all__", []))
        history = self._monthly_history(60)
        forecaster_cls = agentforecast.OnlineForecaster
        forecaster = forecaster_cls(
            backend="river_linear",
            lookback=24,
            horizons=[1, 3, 6],
            strict_mode=True,
        )
        self.assertTrue(hasattr(forecaster, "fit"))
        self.assertTrue(hasattr(forecaster, "predict"))
        self.assertTrue(hasattr(forecaster, "update"))
        forecaster.fit(history.iloc[:48])
        forecast = forecaster.predict()
        self._assert_requested_horizons(forecast)
        forecaster.update(float(history.iloc[48]["y"]))
        forecast_after_update = forecaster.predict()
        self._assert_requested_horizons(forecast_after_update)

    @unittest.skipUnless(SKLEARN_AVAILABLE, "scikit-learn is not installed")
    def test_online_forecaster_direct_mode_supports_supervised_backend(self) -> None:
        self.assertTrue(ONLINE_FORECASTER_AVAILABLE, "agentforecast.OnlineForecaster is not exported.")
        history = self._monthly_history(72)
        forecaster_cls = agentforecast.OnlineForecaster
        init_kwargs = {
            "backend": "ml_ridge",
            "lookback": 24,
            "horizons": [1, 3, 6],
            "strict_mode": True,
        }
        forecaster = None
        for direct_key in ("mode", "forecast_mode", "prediction_mode"):
            try:
                forecaster = forecaster_cls(**init_kwargs, **{direct_key: "direct"})
                break
            except TypeError:
                continue
        if forecaster is None:
            self.fail("OnlineForecaster does not accept a direct-mode keyword such as mode=direct.")
        forecaster.fit(history.iloc[:54])
        forecast = forecaster.predict()
        self._assert_requested_horizons(forecast)
        forecaster.update(float(history.iloc[54]["y"]))
        forecast_after_update = forecaster.predict()
        self._assert_requested_horizons(forecast_after_update)

    def test_strict_mode_rejects_duplicate_timestamps_and_implicit_gap_repair(self) -> None:
        duplicate_frame = pd.DataFrame(
            {
                "ds": pd.date_range("2024-01-01", periods=10, freq="D").tolist()[:5]
                + [pd.Timestamp("2024-01-05")]
                + pd.date_range("2024-01-06", periods=4, freq="D").tolist(),
                "y": list(range(10)),
            }
        )
        gap_frame = pd.DataFrame(
            {
                "ds": [
                    pd.Timestamp("2024-02-01"),
                    pd.Timestamp("2024-02-02"),
                    pd.Timestamp("2024-02-03"),
                    pd.Timestamp("2024-02-04"),
                    pd.Timestamp("2024-02-06"),
                    pd.Timestamp("2024-02-07"),
                    pd.Timestamp("2024-02-08"),
                    pd.Timestamp("2024-02-09"),
                    pd.Timestamp("2024-02-10"),
                    pd.Timestamp("2024-02-11"),
                ],
                "y": list(range(10)),
            }
        )
        with self.assertRaises(AgentForecastError):
            prepare_series_frame(duplicate_frame, strict_mode=True)
        with self.assertRaises(AgentForecastError):
            prepare_series_frame(gap_frame, strict_mode=True)

    def test_prepare_series_frame_respects_max_history_and_reports_cleanup(self) -> None:
        frame = pd.read_csv(public_example_path("airline-passengers"))
        prepared = prepare_series_frame(frame, max_history=24)
        self.assertEqual(len(prepared.history), 24)
        self.assertFalse(prepared.strict_mode)
        self.assertTrue(prepared.cleanup["cleanup_applied"])
        self.assertGreater(prepared.cleanup["history_truncated"], 0)
        self.assertEqual(prepared.cleanup["history_rows_retained"], 24)

    def test_validate_and_clean_series_frame_are_split(self) -> None:
        frame = pd.DataFrame(
            {
                "ds": [
                    pd.Timestamp("2024-01-01"),
                    pd.Timestamp("2024-01-02"),
                    pd.Timestamp("2024-01-04"),
                    pd.Timestamp("2024-01-04"),
                    pd.Timestamp("2024-01-05"),
                    pd.Timestamp("2024-01-06"),
                    pd.Timestamp("2024-01-07"),
                    pd.Timestamp("2024-01-08"),
                    pd.Timestamp("2024-01-09"),
                    pd.Timestamp("2024-01-10"),
                ],
                "y": list(range(10)),
            }
        )
        report = validate_series_frame(frame, strict_mode=True)
        self.assertTrue(report["ok"])
        self.assertFalse(report["strict_ready"])
        self.assertTrue(report["cleaning_recommended"])
        self.assertGreater(report["duplicate_timestamps"], 0)
        self.assertGreater(report["irregular_timestamps"], 0)
        prepared = clean_series_frame(frame)
        self.assertTrue(prepared.cleanup["cleanup_applied"])
        self.assertGreaterEqual(prepared.cleanup["duplicate_timestamps_merged"], 1)

    def test_diagnose_environment_reports_profiles_and_capabilities(self) -> None:
        payload = diagnose_environment()
        self.assertIn("profiles", payload)
        self.assertIn("backend_capabilities", payload)
        self.assertIn("recommended_commands", payload)
        self.assertTrue(any(row["backend_id"] == "ml_ridge" for row in payload["backend_capabilities"]))
        self.assertIn("pack", payload["profiles"])

    def test_build_feature_spec_supports_feature_preset_and_lookback(self) -> None:
        frame = pd.read_csv(dataset_path("gold-exogenous"))
        prepared = prepare_series_frame(frame, max_history=120)
        spec = build_feature_spec(
            prepared.history,
            feature_spec={},
            benchmark_mode=True,
            lookback=32,
        )
        self.assertEqual(spec["feature_preset"], "benchmark_auto")
        self.assertEqual(spec["lookback"], 32)
        self.assertFalse(spec["include_calendar"])
        self.assertTrue(all(lag <= 32 for lag in spec["lags"]))
        self.assertTrue(all(window <= 32 for window in spec["rolling_windows"]))

    def test_forecast_dataset_accepts_custom_feature_spec(self) -> None:
        custom = FeatureSpec(
            lag_points=(1, 2, 7, 14),
            lag_step=14,
            lag_count=3,
            rolling_windows=(3, 7, 14),
            include_tsfresh=TSFRESH_AVAILABLE,
            tsfresh_window=21,
        )
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_dataset('gold-exogenous', backend='ml_ridge', outdir=tmp, feature_spec=custom)
            self.assertEqual(result.feature_spec['lag_step'], 14)
            self.assertEqual(result.feature_spec['lag_count'], 3)
            self.assertIn(14, result.feature_spec['lags'])
            self.assertEqual(result.feature_spec['include_tsfresh'], TSFRESH_AVAILABLE)

    def test_time_series_regression_case_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = shoot('time-series-regression-lab', outdir=tmp)
            self.assertEqual(result.feature_spec['mode'], 'time_series_regression_lab')
            self.assertIn(result.backend_selected, result.candidate_backends)
            self.assertIn('lags', result.feature_spec)

    def test_list_examples_exposes_curated_hub(self) -> None:
        examples = list_examples()
        example_ids = {item['example_id'] for item in examples}
        self.assertIn('first-forecast-pack', example_ids)
        self.assertIn('time-series-as-regression', example_ids)

    def test_demo_examples_builds_site(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / 'examples_generated'
            site = Path(tmp) / 'examples_site'
            payload = demo_examples(runs, site, example_ids=['first-forecast-pack', 'time-series-as-regression'])
            self.assertEqual(payload['example_count'], 2)
            self.assertTrue((runs / 'manifest.json').exists())
            self.assertTrue((site / 'index.html').exists())
            self.assertTrue((site / 'examples' / 'first-forecast-pack.html').exists())
            rebuilt = build_examples_site(runs, site)
            self.assertEqual(rebuilt['entry_count'], 2)
            page = (site / 'examples' / 'first-forecast-pack.html').read_text(encoding='utf-8')
            self.assertIn('Python API first', page)
            self.assertIn('from agentforecast import forecast_dataframe', page)

    def test_prepare_series_frame_preserves_monthly_calendar_frequency(self) -> None:
        frame = pd.read_csv(public_example_path('airline-passengers'))
        prepared = prepare_series_frame(frame)
        self.assertEqual(prepared.inferred_frequency, 'MS')
        self.assertEqual(prepared.cleanup['missing_points_filled'], 0)
        self.assertTrue(prepared.history['ds'].dt.day.eq(1).all())

    def test_forecast_csv_keeps_monthly_future_dates_on_public_example(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = forecast_csv(public_example_path('monthly-car-sales'), backend='naive', outdir=tmp, horizon=3)
            forecast_path = next(Path(tmp).glob('*/data/forecast.csv'))
            forecast = pd.read_csv(forecast_path)
            self.assertEqual(result.inputs['name'], 'monthly_car_sales')
            self.assertEqual(forecast['ds'].tolist(), ['1969-01-01', '1969-02-01', '1969-03-01'])

    def test_compare_backends_on_public_monthly_example_has_nonzero_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = compare_backends_csv(
                public_example_path('airline-passengers'),
                backends=['naive', 'moving_average'],
                outdir=tmp,
                horizon=12,
            )
            self.assertTrue(all(float(row['mae']) > 0 for row in result.leaderboard))

    def test_build_hosted_site_wraps_gallery_card_in_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs = Path(tmp) / 'runs'
            site = Path(tmp) / 'site'
            shoot('sales', outdir=runs)
            build_hosted_site(runs, site)
            text = (site / 'index.html').read_text(encoding='utf-8')
            self.assertIn("class='gallery-card-link' href='cases/sales.html'", text)

    def test_new_cross_domain_dataset_specs_exist(self) -> None:
        for dataset_id in ['gold-exogenous', 'grid-heatwave-stress', 'river-flood-risk', 'outpatient-no-show']:
            spec = get_dataset_spec(dataset_id)
            self.assertTrue(spec.provenance_en)


if __name__ == '__main__':
    unittest.main()
