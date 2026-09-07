from __future__ import annotations
import argparse
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from app.backend.ml.features.terrain import extract_terrain_features
from app.backend.ml.features.weather_grid_loader import (
    SA_LAT_MAX,
    SA_LAT_MIN,
    SA_LON_MAX,
    SA_LON_MIN,
    build_sa_grid_shape,
)

STATIC_CHANNELS = ["elevation", "slope", "aspect_sin", "aspect_cos"]


@dataclass
class StaticDatasetConfig:
    dem_path: str = "app/datasets/processed/static/sa_dem.vrt"
    out_path: str = "app/datasets/processed/static/static_tensor.npz"
    resolution_deg: float = 0.5


def build_static_tensor(cfg: StaticDatasetConfig = StaticDatasetConfig()) -> Path:
    out_path = Path(cfg.out_path)
    if out_path.exists():
        print(f"Static tensor already built — skipping ({out_path})")
        return out_path
    if not Path(cfg.dem_path).exists():
        if cfg.dem_path == StaticDatasetConfig.dem_path:
            from app.backend.ml.features.dem_source import build_dem_vrt

            build_dem_vrt(SA_LON_MIN, SA_LAT_MIN, SA_LON_MAX, SA_LAT_MAX, cfg.dem_path)
        else:
            raise FileNotFoundError(
                f"{cfg.dem_path} not found. Pass a real DEM path with --dem-path, "
                "or omit it to auto-build the default Copernicus DEM VRT."
            )
    H, W = build_sa_grid_shape(cfg.resolution_deg)
    print(f"Extracting terrain features for SA bbox at {H}x{W} resolution")
    terrain = extract_terrain_features(
        dem_path=cfg.dem_path,
        min_lon=SA_LON_MIN,
        min_lat=SA_LAT_MIN,
        max_lon=SA_LON_MAX,
        max_lat=SA_LAT_MAX,
        target_shape=(H, W),
    )
    aspect_rad = np.radians(terrain["aspect"])
    static_tensor = np.stack(
        [
            terrain["elevation"],
            terrain["slope"],
            np.sin(aspect_rad).astype(np.float32),
            np.cos(aspect_rad).astype(np.float32),
        ]
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_path, static_tensor=static_tensor)
    print(
        f"Saved {out_path}: static_tensor {static_tensor.shape} (channels: {STATIC_CHANNELS})"
    )
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dem-path", default=StaticDatasetConfig.dem_path)
    ap.add_argument("--out-path", default=StaticDatasetConfig.out_path)
    ap.add_argument(
        "--resolution-deg", type=float, default=StaticDatasetConfig.resolution_deg
    )
    args = ap.parse_args()
    cfg = StaticDatasetConfig(
        dem_path=args.dem_path,
        out_path=args.out_path,
        resolution_deg=args.resolution_deg,
    )
    build_static_tensor(cfg)


if __name__ == "__main__":
    main()