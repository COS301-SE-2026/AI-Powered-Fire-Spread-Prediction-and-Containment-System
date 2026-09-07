# loads historical fire data for ignition model (think it's for ignition)

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.neighbors import BallTree

here = Path(__file__).resolve()
for cand in (here.parents[2] / "backend_src", here.parents[2]):
    if cand.is_dir() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

from app.backend.src.ai.features import grid_to_fmatrix
from app.backend.src.ai.schema import BURNED, BURNING, FEATURES, LABEL, UNBURNED

EARTH_RADIUS_KM = 6371.0088


def haversine_km(
    lat1: np.ndarray, lon1: np.ndarray, lat2: np.ndarray, lon2: np.ndarray
) -> np.ndarray:
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def cluster_fire_events(
    detections: pd.DataFrame,
    max_gap_km: float = 5.0,
    max_gap_days: float = 4.0,
) -> np.ndarray:
    """union-find clustering of point detections into distinct fire events"""
    n = len(detections)
    lat_rad = np.radians(detections["lat"].to_numpy())
    lon_rad = np.radians(detections["lon"].to_numpy())
    coords_rad = np.column_stack([lat_rad, lon_rad])
    ts = detections["timestamp"].to_numpy()

    max_gap_rad = max_gap_km / EARTH_RADIUS_KM

    tree = BallTree(coords_rad, metric="haversine")

    neighbor_indices = tree.query_radius(coords_rad, r=max_gap_rad)

    max_gap_ns = np.timedelta64(int(max_gap_days * 86400), "s")

    rows, cols = [], []
    for i, neighbors in enumerate(neighbor_indices):
        time_diffs = np.abs(ts[neighbors] - ts[i])
        valid = time_diffs <= max_gap_ns
        for j in neighbors[valid]:
            rows.append(i)
            cols.append(j)

    adjacency = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    _, fire_ids = connected_components(adjacency, directed=False)

    return fire_ids


@dataclass
class FireEvent:
    fire_id: int
    detection: pd.DataFrame
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float
    ticks: list


def build_fire_events(
    detection: pd.DataFrame, fire_ids: np.ndarray, bbox_buffer_km: float = 2.0
) -> list[FireEvent]:
    events = []
    detection = detection.assign(fire_id=fire_ids)
    for fid, grp in detection.groupby("fire_id"):
        grp = grp.sort_values("timestamp")
        buf_deg = bbox_buffer_km / 111.0
        events.append(
            FireEvent(
                fire_id=int(fid),
                detection=grp,
                min_lon=float(grp["lon"].min() - buf_deg),
                min_lat=float(grp["lat"].min() - buf_deg),
                max_lon=float(grp["lon"].max() + buf_deg),
                max_lat=float(grp["lat"].max() + buf_deg),
                ticks=sorted(grp["timestamp"].dt.floor("D").unique()),
            )
        )
    return events


def rasterize_tick(
    detections_today: pd.DataFrame, event: FireEvent, height: int, width: int
) -> np.ndarray:
    """bool height width grid"""
    hit = np.zeros((height, width), dtype=bool)
    if detections_today.empty:
        return hit
    col = (
        (detections_today["lon"].to_numpy() - event.min_lon)
        / (event.max_lon - event.min_lon)
        * width
    ).astype(int)
    row = (
        (event.max_lat - detections_today["lat"].to_numpy())
        / (event.max_lat - event.min_lat)
        * height
    ).astype(int)
    col = np.clip(col, 0, width - 1)
    row = np.clip(row, 0, height - 1)
    hit[row, col] = True
    return hit


def step_burn_state(prev_state: np.ndarray, detected_today: np.ndarray) -> np.ndarray:
    """UNBURNED to BURNING"""
    new_state = prev_state.copy()
    was_burning = prev_state == BURNING
    new_state[was_burning & ~detected_today] = BURNED
    new_state[(prev_state == UNBURNED) & detected_today] = BURNING
    return new_state


class ConstantWeatherProvider:
    """Placeholder weather sthat fixes grids for every tick of every fire.
    Swap in historical weather data"""

    def __init__(self, wind_u=2.0, wind_v=1.0, rel_humidity=30.0, temperature=28.0):
        self.defaults = {
            "wind_u": wind_u,
            "wind_v": wind_v,
            "rel_humidity": rel_humidity,
            "temperature": temperature,
        }

    def prepare_for_fire(self, event: FireEvent, target_shape: tuple[int, int]) -> None:
        # consts req no preface
        pass  # nothing to prefetch - values are fixed

    def fetch(
        self, _min_lon, _min_lat, _max_lon, _max_lat, _timestamp, target_shape
    ) -> dict[str, np.ndarray]:
        height, width = target_shape
        return {
            k: np.full((height, width), v, dtype=np.float32)
            for k, v in self.defaults.items()
        }


class HistoricalWeatherProvider:
    """Base interface for historical and or the reanalysis weather sources.
    prepare_for_fire called once per event, before its tick
    loop runs gets for whole duration of fire. Caches this for per tick
    retruns : wind_u, wind_v, rel_humidity, temperature"""

    def prepare_for_fire(self, event: FireEvent, target_shape: tuple[int, int]) -> None:
        # interface hook
        pass

    def fetch(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        timestamp,
        target_shape: tuple[int, int],
    ) -> dict[str, np.ndarray]:
        raise NotImplementedError("Connect to hitorical weather data")


class OpenMeteoWeatherProvider(HistoricalWeatherProvider):
    """Historical weather through Open-Meteo.
    Caches each per fire call for fire
    """

    def __init__(self, date_buffer_days: int = 1):
        self.date_buffer_days = date_buffer_days
        self._df_by_fire: dict[int, "pd.DataFrame"] = {}
        self._current_fire_id: Optional[int] = None

    def prepare_for_fire(
        self, event: "FireEvent", target_shape: tuple[int, int]
    ) -> None:
        from app.datasets.scripts.fetch_historical_weather import (
            fetch_historical_weather,
        )

        center_lat = (event.min_lat + event.max_lat) / 2.0
        center_lon = (event.min_lon + event.max_lon) / 2.0
        start = (
            pd.Timestamp(event.ticks[0]) - pd.Timedelta(days=self.date_buffer_days)
        ).strftime("%Y-%m-%d")
        end = (
            pd.Timestamp(event.ticks[-1]) + pd.Timedelta(days=self.date_buffer_days)
        ).strftime("%Y-%m-%d")

        df = fetch_historical_weather(
            latitude=center_lat,
            longitude=center_lon,
            start_date=start,
            end_date=end,
            location_name=f"fire_{event.fire_id}",
        )
        if df.empty:
            raise RuntimeError(
                f"fetch_historical_weather() returned no data for fire_id={event.fire_id} "
                f"({center_lat}, {center_lon}, {start}..{end}) - archive API call likely "
                f"failed silently (see its printed error above)."
            )
        self._df_by_fire[event.fire_id] = df
        self._current_fire_id = event.fire_id

    def fetch(
        self, min_lon, min_lat, max_lon, max_lat, timestamp, target_shape
    ) -> dict[str, np.ndarray]:
        from app.datasets.scripts.fetch_historical_weather import (
            get_weather_at_timestamp,
        )

        if (
            self._current_fire_id is None
            or self._current_fire_id not in self._df_by_fire
        ):
            raise RuntimeError(
                "fetch() called before prepare_for_fire() populated a weather "
                "cache for the current fire - build_rows_for_fire should call "
                "prepare_for_fire(event, ...) once before its tick loop."
            )
        df = self._df_by_fire[self._current_fire_id]
        return get_weather_at_timestamp(df, when=timestamp, target_shape=target_shape)


@dataclass
class StaticSourceManifest:
    """get paths to terrain before fire"""

    rows: dict[int, dict]

    @classmethod
    def from_csv(cls, path: str | Path) -> "StaticSourceManifest":
        df = pd.read_csv(path)
        df = df.astype(object).where(pd.notna(df), None)
        return cls(rows={int(r["fire_id"]): r.to_dict() for _, r in df.iterrows()})

    def get(self, fire_id: int) -> dict:
        if fire_id not in self.rows:
            raise KeyError(
                f"No static-source manifest row for fire_id={fire_id}. "
                f"Every clustered fire event needs a pre-fire imagery/DEM "
                f"entry before its features can be computed."
            )
        return self.rows[fire_id]


def load_static_grids_for_fire(
    manifest_row: dict, min_lon, min_lat, max_lon, max_lat, target_shape
) -> dict[str, np.ndarray]:
    """Uses static feature code"""
    from app.backend.ml.features.fuel_load import process_sentinal2_and_worldcover
    from app.backend.ml.features.terrain import extract_terrain_features

    veg = process_sentinal2_and_worldcover(
        b04_path=manifest_row["b04_path"],
        b08_path=manifest_row["b08_path"],
        b11_path=manifest_row["b11_path"],
        scl_path=manifest_row.get("scl_path") or None,
        worldcover_map_path=manifest_row.get("worldcover_path") or None,
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=target_shape,
    )
    terrain = extract_terrain_features(
        dem_path=manifest_row["dem_path"],
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=target_shape,
    )
    return {
        "elevation": terrain["elevation"],
        "slope": terrain["slope"],
        "aspect_sin": (
            terrain["aspect_sin"]
            if "aspect_sin" in terrain
            else np.sin(np.radians(terrain["aspect"]))
        ),
        "aspect_cos": (
            terrain["aspect_cos"]
            if "aspect_cos" in terrain
            else np.cos(np.radians(terrain["aspect"]))
        ),
        "fuel_load": veg["fuel_load"],
        "dryness": veg["dryness"],
    }


def build_rows_for_fire(
    event: FireEvent,
    static_grids: dict[str, np.ndarray],
    weather_provider,
    target_shape: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (x_all [n_rows, len(FEATURES)], y_fire [n_rows])"""
    height, width = target_shape
    burn_state = np.full((height, width), UNBURNED, dtype=np.int64)

    weather_provider.prepare_for_fire(event, target_shape)

    x_parts, y_parts = [], []

    for t_idx, tick in enumerate(event.ticks[:-1]):  # last tick
        detections_today = event.detection[
            event.detection["timestamp"].dt.floor("D") == tick
        ]
        detected_today_mask = rasterize_tick(detections_today, event, height, width)

        weather_grids = weather_provider.fetch(
            event.min_lon,
            event.min_lat,
            event.max_lon,
            event.max_lat,
            tick,
            target_shape,
        )

        # candidate row
        eligible = burn_state == UNBURNED
        if eligible.any():
            x_grid = grid_to_fmatrix(weather_grids, static_grids, burn_state)

            next_tick = event.ticks[t_idx + 1]
            detections_next = event.detection[
                event.detection["timestamp"].dt.floor("D") == next_tick
            ]
            detected_next_mask = rasterize_tick(detections_next, event, height, width)
            ignited_next = (eligible & detected_next_mask).ravel()

            elig_flat = eligible.ravel()
            x_parts.append(x_grid[elig_flat])
            y_parts.append(ignited_next[elig_flat].astype(np.float32))

        # burn_state for next detection
        burn_state = step_burn_state(burn_state, detected_today_mask)

    if not x_parts:
        return np.empty((0, len(FEATURES)), dtype=np.float32), np.empty(
            (0,), dtype=np.float32
        )
    return np.concatenate(x_parts, axis=0), np.concatenate(y_parts, axis=0)


def load_detections(
    csv_path: str, lat_col: str, lon_col: str, date_col: str, time_col: Optional[str]
) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if time_col and time_col in df.columns:
        # FIRMS
        hhmm = df[time_col].astype(str).str.zfill(4)
        ts = (
            pd.to_datetime(df[date_col])
            + pd.to_timedelta(hhmm.str[:2].astype(int), unit="h")
            + pd.to_timedelta(hhmm.str[2:].astype(int), unit="m")
        )
    else:
        ts = pd.to_datetime(df[date_col])
    out = pd.DataFrame(
        {
            "lat": df[lat_col].astype(float),
            "lon": df[lon_col].astype(float),
            "timestamp": ts,
        }
    )
    return out.sort_values("timestamp").reset_index(drop=True)


def _resolve_within_base(
    user_path: str | Path, base_dir: Path | None = None
) -> tuple[Path, Path]:
    """shared resolution and containment check"""
    if base_dir is None:
        base_dir = Path.cwd().resolve()
    else:
        base_dir = Path(base_dir).resolve()

    resolved_path = Path(user_path).resolve()

    try:
        resolved_path.relative_to(base_dir)
    except ValueError:
        raise ValueError(
            f"Security error: Path '{resolved_path}', escapes allowed base_dir '{base_dir}'"
        )
    return resolved_path, base_dir


def validate_input_path(user_path: str | Path, base_dir: Path | None = None) -> Path:
    """validate path about to read from"""
    resolved_path, _ = _resolve_within_base(user_path, base_dir)
    if not resolved_path.is_file():
        raise ValueError(f"input path not exist or isn't a file: '{resolved_path}")
    return resolved_path


def validate_output_path(user_path: str | Path, base_dir: Path | None = None) -> Path:
    """validate path about to write to"""
    resolved_path, _ = _resolve_within_base(user_path, base_dir)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--csv",
        required=True,
        help="raw historical fire detections, e.g. fire_nrt_J2V-C2_77.csv",
    )
    ap.add_argument("--lat-col", default="latitude")
    ap.add_argument("--lon-col", default="longitude")
    ap.add_argument("--date-col", default="acq_date")
    ap.add_argument("--time-col", default="acq_time")
    ap.add_argument(
        "--manifest",
        required=True,
        help="CSV: fire_id -> pre-fire imagery/DEM paths (see StaticSourceManifest)",
    )
    ap.add_argument("--weather", choices=["constant", "historical"], default="constant")
    ap.add_argument(
        "--target-shape",
        type=int,
        nargs=2,
        default=(64, 64),
        metavar=("height", "weight"),
    )
    ap.add_argument("--max-gap-km", type=float, default=5.0)
    ap.add_argument("--max-gap-days", type=float, default=4.0)
    ap.add_argument("--out", default="ignition_dataset.npz")
    ap.add_argument(
        "--base-dir",
        default=None,
        help="Dir all --csv/--manifest/--out paths resolved",
    )
    args = ap.parse_args()

    base_dir = Path(args.base_dir).resolve() if args.base_dir else Path.cwd().resolve()

    csv_path = validate_input_path(args.csv, base_dir)  # NOSONAR
    manifest_path = validate_input_path(args.manifest, base_dir)  # NOSONAR

    if args.weather == "historical":
        weather_provider = OpenMeteoWeatherProvider()
    else:
        weather_provider = ConstantWeatherProvider()

    detections = load_detections(
        str(csv_path), args.lat_col, args.lon_col, args.date_col, args.time_col
    )
    print(f"Loaded {len(detections):,} raw detections from {args.csv}")

    fire_ids = cluster_fire_events(
        detections, max_gap_km=args.max_gap_km, max_gap_days=args.max_gap_days
    )
    n_fires = len(np.unique(fire_ids))
    print(
        f"Clustered into {n_fires} distinct fire events "
        f"(max_gap_km={args.max_gap_km}, max_gap_days={args.max_gap_days})"
    )

    events = build_fire_events(detections, fire_ids)
    manifest = StaticSourceManifest.from_csv(manifest_path)
    target_shape = tuple(args.target_shape)

    x_all, y_all, fid_all = [], [], []
    skipped = []
    for event in events:
        try:
            manifest_row = manifest.get(event.fire_id)
        except KeyError as e:
            skipped.append(event.fire_id)
            print(f"  [skip] fire_id={event.fire_id}: {e}")
            continue

        static_grids = load_static_grids_for_fire(
            manifest_row,
            event.min_lon,
            event.min_lat,
            event.max_lon,
            event.max_lat,
            target_shape,
        )
        x_fire, y_fire = build_rows_for_fire(
            event, static_grids, weather_provider, target_shape
        )
        if len(y_fire) == 0:
            print(
                f"  [empty] fire_id={event.fire_id}: no eligible rows (single-tick fire?)"
            )
            continue

        x_all.append(x_fire)
        y_all.append(y_fire)
        fid_all.append(np.full(len(y_fire), event.fire_id, dtype=np.int64))
        print(
            f"  fire_id={event.fire_id}: {len(event.ticks)} ticks, "
            f"{len(y_fire):,} rows, {y_fire.mean()*100:.2f}% positive"
        )

    if not x_all:
        raise SystemExit("No usable fire events - nothing to write.")

    x_matrix = np.concatenate(x_all, axis=0)
    y_vector = np.concatenate(y_all, axis=0)
    fire_ids_out = np.concatenate(fid_all, axis=0)

    print(
        f"\nTotal: {len(y_vector):,} rows across {len(x_all)} fires "
        f"({len(skipped)} skipped for missing manifest entries)"
    )
    print(f"Overall positive rate: {y_vector.mean()*100:.3f}%")

    out_path = validate_output_path(args.out, base_dir)

    np.savez_compressed(out_path, X=x_matrix, y=y_vector, fire_ids=fire_ids_out)

    meta_path = validate_output_path(out_path.with_suffix(".meta.json"), base_dir)
    meta_path.write_text(  # NOSONAR
        json.dumps(
            {
                "source_csv": str(csv_path),
                "n_fires": len(x_all),
                "n_rows": int(len(y_vector)),
                "features": FEATURES,
                "label": LABEL,
                "target_shape": list(target_shape),
                "weather_source": args.weather,
                "skipped_fire_ids": skipped,
            },
            indent=2,
        )
    )
    print(f"Wrote {out_path} and {meta_path}")


if __name__ == "__main__":
    main()
