# returns wind_u, wind_v, temperature and relative humidity
# gets data from https://archive-api.open-meteo.com/v1/archive:
# "latitude": latitude,
# "longitude": longitude,
# "start_date": start_date,
# "end_date": end_date,
# "hourly": [
#     "temperature_2m",
#     "relative_humidity_2m",
#     "wind_speed_10m",
#     "wind_direction_10m"
# ]
# currently gets only a year's data, because one can't query the fire data for longer than a year

import math
from datetime import datetime
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = DATASETS_DIR / "processed" / "historical_weather"
GRID_OUTPUT_DIR = DATASETS_DIR / "processed" / "historical_weather_grid"

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
]
def calculate_wind_components(
    wind_speed: float, wind_dir_deg: float
) -> tuple[float, float]:
    """converts wind speed m/s and meteorological direction degrees into East-West and North-South vector comps"""

    rad = math.radians(wind_dir_deg)
    # direction from which the wind originates is named
    wind_u = -wind_speed * math.sin(rad)
    wind_v = -wind_speed * math.cos(rad)
    return round(wind_u, 4), round(wind_v, 4)


def fetch_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    location_name: str = "custom_point",
) -> pd.DataFrame:
    """fetches hourly ERA5 reanalysis weahter data from open-meteo archive API"""

    print(f"Fetching historical weather for {location_name} ({latitude}, {longitude})")
    print(f"Period: {start_date} to {end_date}")

    url = ARCHIVE_URL
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": HOURLY_VARS
    }

    try:
        response = httpx.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch weather data: {e}")
        return pd.DataFrame()

    hourly_data = data.get("hourly", {})
    if not hourly_data or "time" not in hourly_data:
        print(f"No hourly data returned")
        return pd.DataFrame()

    df = pd.DataFrame(hourly_data)

    # column naming match weather_adapter
    df.rename(
        columns={
            "time": "datetime",
            "temperature_2m": "temperature",
            "relative_humidity_2m": "relative_humidity",
            "wind_speed_10m": "wind_speed",
            "wind_direction_10m": "wind_direction",
        },
        inplace=True,
    )

    # dryness index
    df["dryness"] = np.clip(
        (100 - df["relative_humidity"] + df["temperature"]) / 100.0, 0.0, 1.0
    ).round(4)

    # u and v wind vector
    u_list, v_list = [], []
    for _, row in df.iterrows():
        u, v = calculate_wind_components(row["wind_speed"], row["wind_direction"])
        u_list.append(u)
        v_list.append(v)

    df["wind_u"] = u_list
    df["wind_v"] = v_list

    # location
    df["latitude"] = latitude
    df["longitude"] = longitude

    # export csv
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"weather_{location_name}_{start_date}_to_{end_date}.csv"
    df.to_csv(out_file, index=False)

    print(f"Saved {len(df):,} hourly weather records to: {out_file}")
    return df


def get_weather_at_timestamp(
    df_weather: pd.DataFrame,
    when: datetime,
    target_shape: tuple[int, int] = (64, 64),
) -> dict[str, np.ndarray]:
    """Looks up nearest hourly record to 'when' in already gotten weather dataframe and puts into
    (H, W) gris. Matches key names used - exclude 'dryness

    Call fetch_historical_weather() once for every fire as not to make API call redundent
    """

    if df_weather.empty:
        raise ValueError(
            "df_weather is empty, fetch_historical_weather() could've failed silently"
        )

    H, W = target_shape

    dt_series = pd.to_datetime(df_weather["datetime"])
    when_ts = pd.Timestamp(when)
    index = (dt_series - when_ts).abs().idxmin()
    row = df_weather.loc[index]

    return {
        "wind_u": np.full((H, W), float(row["wind_u"]), dtype=np.float32),
        "wind_v": np.full((H, W), float(row["wind_v"]), dtype=np.float32),
        "temperature": np.full((H, W), float(row["temperature"]), dtype=np.float32),
        "rel_humidity": np.full(
            (H, W), float(row["relative_humidity"]), dtype=np.float32
        ),
    }

"""
Grid fetching stuff below. 
We need the whole SA mesh over many years rather than just a single point. 
Functions above are not changed in terms of functionality.
"""

def calculate_wind_components_vectorized(
    wind_speed: np.ndarray, wind_dir_deg: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Same formula as above, but vectorized for numpy arrays.
    """
    rad = np.radians(wind_dir_deg)
    # direction from which the wind originates is named
    wind_u = -wind_speed * np.sin(rad)
    wind_v = -wind_speed * np.cos(rad)
    return np.round(wind_u, 4), np.round(wind_v, 4)

def build_sa_grid_coords(resolution_deg: float = 0.5) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Builds a grid of lat/lon coordinates covering South Africa.
    Returns two 2D arrays: latitudes and longitudes.
    """
    # South Africa bounding box
    lat_min, lat_max = -35.0, -22.0
    lon_min, lon_max = 16.0, 33.0
    lats = np.arange(lat_max, lat_min - resolution_deg, -resolution_deg)
    lons = np.arange(lon_min, lon_max + resolution_deg, resolution_deg)
    lat_grid, lon_grid = np.meshgrid(lats, lons, indexing='ij')
    return list(zip(lat_grid.ravel().tolist(), lon_grid.ravel().tolist()))

import time

def fetch_historical_weather_grid_year(
    coords: list[tuple[float, float]],
    year: int,
    chunk_size: int = 10,
    region_name: str = "south_africa",
    max_retries: int = 4,
    base_delay: float = 8.0,
) -> pd.DataFrame:
    start_date, end_date = f"{year}-01-01", f"{year}-12-31"
    out_file = GRID_OUTPUT_DIR / f"weather_grid_{region_name}_{year}.csv"
    GRID_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # resume support: skip coords already written from a previous partial run
    done_coords = set()
    if out_file.exists():
        existing = pd.read_csv(out_file, usecols=["latitude", "longitude"])
        done_coords = set(zip(existing["latitude"].round(4), existing["longitude"].round(4)))
        print(f"Resuming: {len(done_coords)} points already saved in {out_file}")

    remaining = [c for c in coords if (round(c[0], 4), round(c[1], 4)) not in done_coords]
    print(f"Fetching historical weather grid for {region_name} ({len(remaining)}/{len(coords)} points remaining) for year {year}")

    n_chunks = (len(remaining) + chunk_size - 1) // chunk_size
    header_written = out_file.exists()

    for i in range(0, len(remaining), chunk_size):
        chunk = remaining[i:i + chunk_size]
        chunk_num = i // chunk_size + 1
        print(f"  chunk {chunk_num}/{n_chunks} ({len(chunk)} points)...")
        latitudes, longitudes = zip(*chunk)
        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": HOURLY_VARS
        }

        data = None
        for attempt in range(max_retries):
            try:
                response = httpx.get(ARCHIVE_URL, params=params, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = base_delay * (2 ** attempt)
                    print(f"    429 rate limited, retrying in {wait:.0f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    print(f"    HTTP error for chunk {chunk_num}: {e}")
                    break
            except Exception as e:
                print(f"    Failed to fetch weather data for chunk {chunk_num}: {e}")
                break

        if data is None:
            print(f"    giving up on chunk {chunk_num} for now — rerun later to pick up remaining points")
            time.sleep(base_delay)
            continue

        points = data if isinstance(data, list) else [data]
        chunk_frames = []
        for (lat, lon), point in zip(chunk, points):
            hourly = point.get("hourly", {})
            if not hourly or "time" not in hourly:
                print(f"No hourly data for ({lat}, {lon}) — skipping")
                continue

            df = pd.DataFrame(hourly)
            df.rename(
                columns={
                    "time": "datetime",
                    "temperature_2m": "temperature",
                    "relative_humidity_2m": "relative_humidity",
                    "wind_speed_10m": "wind_speed",
                    "wind_direction_10m": "wind_direction",
                },
                inplace=True,
            )
            df["wind_u"], df["wind_v"] = calculate_wind_components_vectorized(
                df["wind_speed"].to_numpy(), df["wind_direction"].to_numpy()
            )
            df["dryness"] = np.clip(
                (100 - df["relative_humidity"] + df["temperature"]) / 100.0, 0.0, 1.0
            ).round(4)
            df["latitude"] = lat
            df["longitude"] = lon
            chunk_frames.append(df)

        if chunk_frames:
            chunk_result = pd.concat(chunk_frames, ignore_index=True)
            chunk_result.to_csv(out_file, mode="a", header=not header_written, index=False)
            header_written = True
            print(f"    saved {len(chunk_result):,} rows -> {out_file}")

        time.sleep(base_delay)

    return pd.read_csv(out_file) if out_file.exists() else pd.DataFrame()
    start_date, end_date = f"{year}-01-01", f"{year}-12-31"
    print(f"Fetching historical weather grid for {region_name} ({len(coords)} points) for year {year}")

    frames = []
    n_chunks = (len(coords) + chunk_size - 1) // chunk_size
    for i in range(0, len(coords), chunk_size):
        chunk = coords[i:i + chunk_size]
        chunk_num = i // chunk_size + 1
        print(f"  chunk {chunk_num}/{n_chunks} ({len(chunk)} points)...")
        latitudes, longitudes = zip(*chunk)
        params = {
            "latitude": latitudes,
            "longitude": longitudes,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": HOURLY_VARS
        }

        data = None
        for attempt in range(max_retries):
            try:
                response = httpx.get(ARCHIVE_URL, params=params, timeout=120.0)
                response.raise_for_status()
                data = response.json()
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = base_delay * (2 ** attempt)
                    print(f"    429 rate limited, retrying in {wait:.0f}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    print(f"    HTTP error for chunk {chunk_num}: {e}")
                    break
            except Exception as e:
                print(f"    Failed to fetch weather data for chunk {chunk_num}: {e}")
                break

        if data is None:
            print(f"    giving up on chunk {chunk_num} after {max_retries} attempts")
            continue

        points = data if isinstance(data, list) else [data]
        for (lat, lon), point in zip(chunk, points):
            hourly = point.get("hourly", {})
            if not hourly or "time" not in hourly:
                print(f"No hourly data for ({lat}, {lon}) — skipping")
                continue

            df = pd.DataFrame(hourly)
            df.rename(
                columns={
                    "time": "datetime",
                    "temperature_2m": "temperature",
                    "relative_humidity_2m": "relative_humidity",
                    "wind_speed_10m": "wind_speed",
                    "wind_direction_10m": "wind_direction",
                },
                inplace=True,
            )
            df["wind_u"], df["wind_v"] = calculate_wind_components_vectorized(
                df["wind_speed"].to_numpy(), df["wind_direction"].to_numpy()
            )
            df["dryness"] = np.clip(
                (100 - df["relative_humidity"] + df["temperature"]) / 100.0, 0.0, 1.0
            ).round(4)
            df["latitude"] = lat
            df["longitude"] = lon
            frames.append(df)

        time.sleep(base_delay)  # pace ourselves even on success, to avoid tripping the limit again

    if not frames:
        print("No data fetched for any coordinates.")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    GRID_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = GRID_OUTPUT_DIR / f"weather_grid_{region_name}_{year}.csv"
    result.to_csv(out_file, index=False)
    print(f"Saved {len(result):,} hourly weather records to: {out_file}")
    return result
def fetch_historical_weather_grid_sa(
    start_year: int, end_year: int, resolution_deg: float = 0.5
)-> None:
    """
    Fetches historical weather data for a grid covering South Africa for a range of years.
    """
    coords = build_sa_grid_coords(resolution_deg)
    print(f"Fetching weather data for {len(coords)} grid points at {resolution_deg}° resolution from {start_year} to {end_year}")
    for year in range(start_year, end_year + 1):
        out_file = GRID_OUTPUT_DIR / f"weather_grid_south_africa_{year}.csv"
        if out_file.exists():
            print(f"Data for year {year} already exists at {out_file}, skipping.")
            continue
        fetch_historical_weather_grid_year(coords, year, region_name="south_africa")


if __name__ == "__main__":
    # fetch one year of weather for Pta, SA
    TEST_LAT = -25.7479
    TEST_LON = 28.2293
    START = "2024-01-01"
    END = "2024-12-31"

    df_weather = fetch_historical_weather(
        latitude=TEST_LAT,
        longitude=TEST_LON,
        start_date=START,
        end_date=END,
        location_name="pretoria",
    )
    fetch_historical_weather_grid_sa(start_year=2006, end_year=2025)
