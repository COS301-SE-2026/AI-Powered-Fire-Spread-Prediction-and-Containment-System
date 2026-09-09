import httpx
import numpy as np


async def fetch_realtime_weather_features(
    center_lat: float, center_lon: float, target_shape: tuple[int, int] = (64, 64)
) -> dict[str, np.ndarray]:
    """Fetches real-time weather telementry and builds weather matrices matching spacial target shape"""
    H, W = target_shape

    # Open-Meteo REST API
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={center_lat}&longitude={center_lon}&"
        f"current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=5.0)
        data = response.json()

    current = data.get("current", {})
    temp_c = float(current.get("temperature_2m", 25.0))
    rh_pct = float(current.get("relative_humidity_2m", 30.0))
    wind_speed = float(current.get("wind_speed_10m", 5.0))
    wind_dir_deg = float(current.get("wind_direction_10m", 0.0))

    # dryness factor
    scalar_dryness = float(np.clip((100.0 - rh_pct + temp_c) / 100.0, 0.0, 1.0))

    # wind magnitude and angle inteast-west (U) and north-south (V) vectors
    wind_rad = np.radians(wind_dir_deg)
    u_val = float(-wind_speed * np.sin(wind_rad))
    v_val = float(-wind_speed * np.cos(wind_rad))

    return {
        "dryness": np.full((H, W), scalar_dryness, dtype=np.float32),
        "wind_u": np.full((H, W), u_val, dtype=np.float32),
        "wind_v": np.full((H, W), v_val, dtype=np.float32),
        "temperature": np.full((H, W), temp_c, dtype=np.float32),
        "rel_humidity": np.full((H, W), rh_pct / 100.0, dtype=np.float32)
    }
