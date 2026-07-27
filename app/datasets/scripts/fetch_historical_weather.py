import httpx
import numpy as np
import pandas as pd
from pathlib import Path
import math

SCRIPT_DIR = Path(__file__).resolve().parent
DATASETS_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = DATASETS_DIR / "processed" / "historical_weather"

def calculate_wind_components(wind_speed:float, wind_dir_deg: float) -> tuple[float, float]:
    """converts wind speed m/s and meteorological direction degrees into East-West and North-South vector comps"""

    rad = math.radians(wind_dir_deg)
    #direction from which the wind originates is named
    wind_u = -wind_speed * math.sin(rad)
    wind_v = -wind_speed * math.cos(rad)
    return round(wind_u, 4), round(wind_v, 4)

def fetch_historical_weather(
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
        location_name: str = "custom_point"
) -> pd.DataFrame:
    """fetches hourly ERA5 reanalysis weahter data from open-meteo archive API"""

    print(f"Fetching historical weather for {location_name} ({latitude}, {longitude})")
    print(f"Period: {start_date} to {end_date}")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m"
        ]
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

    #column naming match weather_adapter
    df.rename(columns={
        "time": "datetime",
        "temperature_2m": "temperature",
        "relative_humidity_2m": "relative_humidity",
        "wind_speed_10m": "wind_speed",
        "wind_direction_10m": "wind_direction"
    }, inplace=True)

    #dryness index
    df["drynes"] = np.clip((100 - df["relative_humidity"] + df["temperature"]) / 100.0, 0.0, 1.0).round(4)

    #u and v wind vector
    u_list, v_list = [], []
    for _, row in df.iterrows():
        u, v = calculate_wind_components(row["wind_speed"], row["wind_direction"])
        u_list.append(u)
        v_list.append(v)

    df["wind_u"] = u_list
    df["wind_v"] = v_list

    #location
    df["latitude"] = latitude
    df["longitude"] = longitude

    #export csv
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"weather_{location_name}_{start_date}_to_{end_date}.csv"
    df.to_csv(out_file, index=False)

    print(f"Saved {len(df):,} hourly weather records to: {out_file}")
    return df

if __name__ == "__main__":
    #fetch one year of weather for Pta, SA
    TEST_LAT = -25.7479
    TEST_LON = 28.2293
    START = "2024-01-01"
    END = "2024-12-31"

    df_weather = fetch_historical_weather(
        latitude=TEST_LAT,
        longitude=TEST_LON,
        start_date=START,
        end_date=END,
        location_name="pretoria"
    )