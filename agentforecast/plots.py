from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_forecast(history: pd.DataFrame, forecast: pd.DataFrame, *, title: str, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    x_hist = pd.to_datetime(history["ds"]).to_numpy()
    x_fcst = pd.to_datetime(forecast["ds"]).to_numpy()
    ax.plot(x_hist, np.asarray(history["y"], dtype=float), label="history", linewidth=2)
    ax.plot(x_fcst, np.asarray(forecast["yhat"], dtype=float), label="forecast", linewidth=2)
    if "lower_90" in forecast.columns and "upper_90" in forecast.columns:
        ax.fill_between(x_fcst, np.asarray(forecast["lower_90"], dtype=float), np.asarray(forecast["upper_90"], dtype=float), alpha=0.18, label="90% interval")
    if "lower_80" in forecast.columns and "upper_80" in forecast.columns:
        ax.fill_between(x_fcst, np.asarray(forecast["lower_80"], dtype=float), np.asarray(forecast["upper_80"], dtype=float), alpha=0.25, label="80% interval")
    ax.set_title(title)
    ax.set_xlabel("time")
    ax.set_ylabel("value")
    ax.legend()
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_forecast_card(history: pd.DataFrame, forecast: pd.DataFrame, *, title: str, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    x_hist = pd.to_datetime(history["ds"]).to_numpy()
    x_fcst = pd.to_datetime(forecast["ds"]).to_numpy()
    ax.plot(x_hist, np.asarray(history["y"], dtype=float), linewidth=2)
    ax.plot(x_fcst, np.asarray(forecast["yhat"], dtype=float), linewidth=2)
    if "lower_90" in forecast.columns and "upper_90" in forecast.columns:
        ax.fill_between(x_fcst, np.asarray(forecast["lower_90"], dtype=float), np.asarray(forecast["upper_90"], dtype=float), alpha=0.18)
    latest = float(history["y"].iloc[-1])
    end = float(forecast["yhat"].iloc[-1])
    delta = end - latest
    ax.set_title(f"{title}\nlatest={latest:.2f} | end={end:.2f} | delta={delta:+.2f}")
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_leaderboard_card(leaderboard: pd.DataFrame, *, title: str, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, max(2.8, 0.55 * len(leaderboard) + 1.8)))
    ax.axis("off")
    rows = [f"{idx+1}. {row.backend_id} | MAE={row.mae:.3f} | RMSE={row.rmse:.3f}" for idx, row in enumerate(leaderboard.itertuples())]
    text = title + "\n\n" + "\n".join(rows[:8])
    ax.text(0.02, 0.98, text, va="top", ha="left", family="monospace", fontsize=10)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_backend_comparison(history: pd.DataFrame, forecast_map: dict[str, pd.DataFrame], *, title: str, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(pd.to_datetime(history["ds"]).to_numpy(), np.asarray(history["y"], dtype=float), linewidth=2, label="history")
    for backend_id, forecast in forecast_map.items():
        ax.plot(pd.to_datetime(forecast["ds"]).to_numpy(), np.asarray(forecast["yhat"], dtype=float), linewidth=1.8, label=backend_id)
    ax.set_title(title)
    ax.grid(True, alpha=0.2)
    ax.legend(ncol=2)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_delta_card(leaderboard: pd.DataFrame, *, title: str, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    ax.axis("off")
    if len(leaderboard) >= 2:
        winner = leaderboard.iloc[0]
        runner = leaderboard.iloc[1]
        delta = float(runner["mae"] - winner["mae"])
        lines = [
            title,
            "",
            f"winner: {winner['backend_id']}  mae={winner['mae']:.3f}",
            f"runner: {runner['backend_id']}  mae={runner['mae']:.3f}",
            f"mae gap: {delta:+.3f}",
        ]
    else:
        winner = leaderboard.iloc[0]
        lines = [title, "", f"only backend: {winner['backend_id']}  mae={winner['mae']:.3f}"]
    ax.text(0.03, 0.97, "\n".join(lines), va="top", ha="left", family="monospace", fontsize=11)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_drift_alert_card(*, title: str, backend: str, rolling_mae: float | None, base_mae: float | None, drift_ratio: float, alert: bool, output_path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.axis("off")
    status = "ALERT" if alert else "stable"
    lines = [
        title,
        "",
        f"backend: {backend}",
        f"base_mae: {base_mae if base_mae is not None else 'n/a'}",
        f"rolling_mae: {rolling_mae if rolling_mae is not None else 'n/a'}",
        f"drift_ratio: {drift_ratio:.3f}",
        f"status: {status}",
    ]
    ax.text(0.03, 0.97, "\n".join(lines), va="top", ha="left", family="monospace", fontsize=11)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180)
    plt.close(fig)
