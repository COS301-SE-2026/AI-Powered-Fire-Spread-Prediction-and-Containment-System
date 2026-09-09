from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.backend.ml.features.weather_grid_loader import load_weather_grid_csv
from app.backend.ml.features.temporal_targets import TemporalTargetBuilder
from app.backend.ml.features.delta_targets import DeltaComputer


@dataclass
class WeatherDatasetConfig:
    raw_grid_dir: str = "/app/datasets/processed/historical_weather_grid"
    out_dir: str = "/app/datasets/processed/weather_tensors"
    substeps_per_hour: int = 4
    resolution_deg: float = 0.5


def build_weather_tensors_for_year(
    year: int, cfg: WeatherDatasetConfig = WeatherDatasetConfig()
) -> Path | None:
    csv_path = Path(cfg.raw_grid_dir) / f"weather_grid_south_africa_{year}.csv"
    if not csv_path.exists():
        print(
            f"{csv_path} not found — run fetch_historical_weather_grid_sa first. Skipping {year}."
        )
        return None
    out_path = Path(cfg.out_dir) / f"weather_tensors_{year}.npz"
    if out_path.exists():
        print(f"{year} already built, skipping ({out_path})")
        return out_path
    print("Loading {csv_path}")
    hourly_tensor, hourly_timestamps = load_weather_grid_csv(
        csv_path, cfg.resolution_deg
    )

    hourly_deltas = DeltaComputer().compute_deltas(hourly_tensor)

    render_builder = TemporalTargetBuilder(substeps_per_hour=cfg.substeps_per_hour)
    quarter_tensor = render_builder.interpolate(hourly_tensor)
    quarter_timestamps = render_builder.quarter_hourly_timestamps(hourly_timestamps)

    Path(cfg.out_dir).mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out_path,
        hourly_tensor=hourly_tensor,
        hourly_timestamps=np.array(hourly_timestamps, dtype="U19"),
        hourly_deltas=hourly_deltas,
        quarter_tensor=quarter_tensor,
        quarter_timestamps=np.array(quarter_timestamps, dtype="U25"),
    )
    print(
        f"Saved {out_path}: hourly {hourly_tensor.shape}, hourly_deltas {hourly_deltas.shape}, "
        f"quarter (render-only) {quarter_tensor.shape}"
    )
    return out_path


def build_all_available_years(
    cfg: WeatherDatasetConfig = WeatherDatasetConfig(),
) -> list[Path]:
    built = []
    for csv_path in sorted(
        Path(cfg.raw_grid_dir).glob("weather_grid_south_africa_*.csv")
    ):
        year = int(csv_path.stem.split("_")[-1])
        result = build_weather_tensors_for_year(year, cfg)
        if result is not None:
            built.append(result)
    return built


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", default=WeatherDatasetConfig.raw_grid_dir)
    ap.add_argument("--out-dir", default=WeatherDatasetConfig.out_dir)
    ap.add_argument("--substeps-per-hour", type=int, default=4)
    ap.add_argument("--resolution-deg", type=float, default=0.5)
    args = ap.parse_args()

    cfg = WeatherDatasetConfig(
        raw_grid_dir=args.raw_dir,
        out_dir=args.out_dir,
        substeps_per_hour=args.substeps_per_hour,
        resolution_deg=args.resolution_deg,
    )
    built = build_all_available_years(cfg)
    print(f"built {len(built)} year(s)")


if __name__ == "__main__":
    main()