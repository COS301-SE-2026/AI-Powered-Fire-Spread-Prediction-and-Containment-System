# real data, should be able to replace synthetic data
# VIIRS active-fire hotspot detections and historical weather

from __future__ import annotations

from dataclasses import dataclass

import os
import numpy as np
import pandas as pd

from app.backend.src.ai.features import grid_to_fmatrix
from app.backend.src.ai.inspect_fire import inspect_fire_events
from app.backend.src.ai.schema import BURNED, BURNING, UNBURNED
from app.datasets.scripts.fetch_historical_weather import (
    fetch_historical_weather,
    get_weather_at_timestamp,
)
from app.backend.ml.features.fuel_load import process_sentinal2_and_worldcover
from app.backend.ml.features.terrain import extract_terrain_features

os.environ.setdefault("AWS_NO_SIGN_REQUEST", "YES")


@dataclass
class RealDatasetConfig:
    hotspots_csv: str = "app/datasets/raw_data/fire_nrt_J2V-C2_778685.csv"

    manifest_csv: str = "app/datasets/raw_data/static_manifest_test.csv"

    worldcover_path: str = "app/datasets/raw_data/worldcover.tif"
    b04_path: str = "app/datasets/raw_data/b04.tif"
    b08_path: str = "app/datasets/raw_data/b08.tif"
    b11_path: str = "app/datasets/raw_data/b11.tif"
    dem_path: str = "app/datasets/raw_data/dem.tif"

    target_shape: tuple[int, int] = (64, 64)
    bbox_buffer_deg: float = 0.02

    # low-confidence detections, false positives, remove as starting point
    min_confidence: set[str] = None

    # spatiotemporal clustering thresholds grouping pnts into fire events
    cluster_distance_km: float = 5.0
    cluster_time_gap_days: float = 4.0
    min_ticks: int = 2

    candidate_dilation: int | None = None


def _load_hotspots(cfg: RealDatasetConfig) -> pd.DataFrame:
    """Loads VIIRS csv, builds datetime column, applies confidence filter"""
    df = pd.read_csv(cfg.hotspots_csv, dtype={"acq_time": str})

    # pad to HHMM before parsing
    df["acq_time"] = df["acq_time"].str.zfill(4)
    df["datetime"] = pd.to_datetime(
        df["acq_date"] + " " + df["acq_time"].str[:2] + ":" + df["acq_time"].str[2:],
        format="%Y-%m-%d %H:%M",
    )

    if cfg.min_confidence:
        df = df[df["confidence"].isin(cfg.min_confidence)]

    return df.sort_values("datetime").reset_index(drop=True)


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def _cluster_into_fire_events(df: pd.DataFrame, cfg: RealDatasetConfig) -> pd.Series:
    """Group raw hotspot detections into distinct fire events: merge into same fire if within cluster_distance_km" and within cluster_time_gap_days

    Will need to change to scikit-learn DBSCAN with havrsine metric or KD-tree windowed search when more points
    """

    n = len(df)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    lats = df["latitude"].to_numpy()
    lons = df["longitude"].to_numpy()
    times = df["datetime"].to_numpy()
    time_gap = np.timedelta64(int(cfg.cluster_time_gap_days * 24), "h")

    # sort by time
    order = np.argsort(times)
    for a_pos in range(1, n):
        i = order[a_pos]
        for b_pos in range(a_pos - 1, -1, -1):
            j = order[b_pos]
            if times[i] - times[j] > time_gap:
                break
            if (
                _haversine_km(lats[i], lons[i], lats[j], lons[j])
                <= cfg.cluster_distance_km
            ):
                union(i, j)

    roots = [find(i) for i in range(n)]
    return pd.Series(roots, index=df.index, name="fire_id").astype(np.int64)


def _optional(value) -> str | None:
    """Manifest blanks read back as '' or NaN; both mean 'stream from S3'."""
    return value if isinstance(value, str) and value.strip() else None


def _static_features_for_fire(
    cfg, row, min_lon, min_lat, max_lon, max_lat
) -> dict[str, np.ndarray]:
    terrain = extract_terrain_features(
        dem_path=row["dem_path"],
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=cfg.target_shape,
    )

    veg = process_sentinal2_and_worldcover(
        worldcover_map_path=_optional(row.get("worldcover_path")),
        b04_path=row["b04_path"],
        b08_path=row["b08_path"],
        b11_path=row["b11_path"],
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=cfg.target_shape,
    )

    aspect_rad = np.radians(terrain["aspect"])
    return {
        "elevation": terrain["elevation"],
        "slope": terrain["slope"],
        "aspect_sin": np.sin(aspect_rad).astype(np.float32),
        "aspect_cos": np.cos(aspect_rad).astype(np.float32),
        "fuel_load": veg["fuel_load"],
        "dryness": veg["dryness"],
    }


def _rasterize_points(
    lats: np.ndarray,
    lons: np.ndarray,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    target_shape: tuple[int, int],
) -> np.ndarray:
    """Bins point detection to bool (H, W) grid over bounding box"""
    H, W = target_shape
    grid = np.zeros((H, W), dtype=bool)
    if len(lats) == 0:
        return grid

    col = ((lons - min_lon) / (max_lon - min_lon) * W).astype(int)
    row = ((max_lat - lats) / (max_lat - min_lat) * H).astype(int)
    valid = (col >= 0) & (col < W) & (row >= 0) & (row < H)
    grid[row[valid], col[valid]] = True
    return grid


def candidate_mask(burn: np.ndarray, dilation: int | None) -> np.ndarray:
    unburned = burn == UNBURNED

    if dilation is None:
        return unburned

    from scipy.ndimage import binary_dilation

    near_fire = binary_dilation(burn == BURNING, iterations=dilation)

    return unburned & near_fire


def load_real_dataset(
    cfg: RealDatasetConfig = RealDatasetConfig(),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns X [N, n_features], y [N], fire_ids [N] same contract as generate_synthetic_dataset(). Candidate rows = UNBURNED cells only"""

    df = _load_hotspots(cfg)

    manifest = pd.read_csv(cfg.manifest_csv).set_index("fire_id")

    events = inspect_fire_events(
        cfg.hotspots_csv,
        max_gap_km=cfg.cluster_distance_km,
        max_gap_days=cfg.cluster_time_gap_days,
        min_ticks=cfg.min_ticks,
        limit=0,
    )

    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    id_parts: list[np.ndarray] = []

    n_used = 0
    for event in events:
        if event.fire_id not in manifest.index:
            continue

        row = manifest.loc[event.fire_id]

        min_lon = event.min_lon - cfg.bbox_buffer_deg
        max_lon = event.max_lon + cfg.bbox_buffer_deg
        min_lat = event.min_lat - cfg.bbox_buffer_deg
        max_lat = event.max_lat + cfg.bbox_buffer_deg

        in_event = (
            df["longitude"].between(min_lon, max_lon)
            & df["latitude"].between(min_lat, max_lat)
            & df["datetime"].between(
                pd.Timestamp(event.ticks[0]), pd.Timestamp(event.ticks[-1])
            )
        )

        fire_df = df[in_event].sort_values("datetime")

        daily = [g for _, g in fire_df.groupby(fire_df["acq_date"])]
        if len(daily) < 2:
            continue

        static = _static_features_for_fire(cfg, row, min_lon, min_lat, max_lon, max_lat)

        df_weather = fetch_historical_weather(
            latitude=(min_lat + max_lat) / 2.0,
            longitude=(min_lon + max_lon) / 2.0,
            start_date=fire_df["acq_date"].min(),
            end_date=fire_df["acq_date"].max(),
            location_name=f"fire_{event.fire_id}",
        )

        if df_weather.empty:
            continue

        burn = np.zeros(cfg.target_shape, dtype=np.int8)

        for i in range(len(daily) - 1):
            day_t, day_t1 = daily[i], daily[i + 1]

            hotspots_t = _rasterize_points(
                day_t["latitude"].to_numpy(),
                day_t["longitude"].to_numpy(),
                min_lon,
                min_lat,
                max_lon,
                max_lat,
                cfg.target_shape,
            )

            hotspots_t1 = _rasterize_points(
                day_t1["latitude"].to_numpy(),
                day_t1["longitude"].to_numpy(),
                min_lon,
                min_lat,
                max_lon,
                max_lat,
                cfg.target_shape,
            )

            burn[hotspots_t] = BURNING

            weather = get_weather_at_timestamp(
                df_weather,
                when=day_t["datetime"].iloc[0],
                target_shape=cfg.target_shape,
            )

            ignited_by_t1 = hotspots_t1 & ~hotspots_t

            x_tick = grid_to_fmatrix(weather, static, burn)
            mask = candidate_mask(burn, cfg.candidate_dilation).ravel()

            if not mask.any():
                continue

            x_parts.append(x_tick[mask])
            y_parts.append(ignited_by_t1.ravel()[mask].astype(np.int8))
            id_parts.append(
                np.full(int(mask.sum()), int(event.fire_id), dtype=np.int64)
            )

            burn[burn == BURNING] = BURNED
            burn[hotspots_t1] = BURNING

        n_used += 1

    if not x_parts:
        raise RuntimeError(
            "No usable fires. Check to see if manifest fire_ids match the clustering"
        )

    return (
        np.concatenate(x_parts),
        np.concatenate(y_parts),
        np.concatenate(id_parts),
    )
