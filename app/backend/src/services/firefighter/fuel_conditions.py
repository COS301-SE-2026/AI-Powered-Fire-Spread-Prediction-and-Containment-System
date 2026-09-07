import math
import requests

MM_TO_KBDI = 3.937
LITTER_INTERCEPT_MM = 5.08
KBDI_MAX = 800.0

FDI_BANDS = [
    (45, "LOW", "blue"),
    (60, "MODERATE", "green"),
    (75, "DANGEROUS", "yellow"),
    (90, "VERY DANGEROUS", "orange"),
    (101, "EXTREMELY DANGEROUS", "red"),
]

# how each fuel type responds to rain
FUEL_REPONSE_TAU = {"grass": 3.0, "shrub": 7.0, "plantation": 21.0}

DIRECTIONS = ["N", 'NNE', "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

def compass(deg: float) -> str:
    return DIRECTIONS[round((deg%360) / 22.5) % 16]

def compute_kbdi(daily_precipitation_mm, daily_tempmax_c, annual_rain_mm: float = 650.0, start: float = 400.0) -> list[float]:
    """
    The Keetch-Bryam Drought INdex over a daily series
    0 => saturated
    800 => max drought
    Returns whole series for a 30 trend
    """
    kbdi = start
    series = []

    for rain, tmax in zip(daily_precipitation_mm, daily_tempmax_c):
        rain = rain or 0.0
        tmax = tmax if tmax is not None else 25.0

        net_rain = max(0.0, rain - LITTER_INTERCEPT_MM)
        kbdi = max(0.0, kbdi - net_rain * MM_TO_KBDI)

        drying = ((KBDI_MAX - kbdi) * (0.968 * math.exp(0.0486 * tmax) - 8.30) / (1.0 + 10.88 * math.exp(-0.0441 * annual_rain_mm))) * 1e-3

        kbdi = min(KBDI_MAX, kbdi + drying)
        series.append(round(kbdi, 1))

    return series

def lowveld_fdi(temp_c: float, rh_pct: float, wind_kmh: float, kbdi: float) -> float:
    """
    Lowveld danger index
    """

    bi = max(0.0, min(100.0, (temp_c - rh_pct / 1.7) + 30.0))

    if wind_kmh <= 5:
        wind_factor = 1.0
    elif wind_kmh <= 15:
        wind_factor = 1.1
    elif wind_kmh <= 25:
        wind_factor = 1.25
    elif wind_kmh <= 40:
        wind_factor = 1.4
    else:
        wind_factor = 1.5

    drought_factor = 0.85 + 0.3 * (kbdi / KBDI_MAX)
    return round(max(0.0, min(100.0, bi * wind_factor * drought_factor)), 1)

def fdi_bands(fdi: float) -> tuple[str, str]:
    for threshold, label, color in FDI_BANDS:
        if fdi < threshold:
            return label, color
    return "EXTREMELY DANGEROUS", "red"

def days_since_rain(daily_precip_mm, threshold_mm: float = 1.0) -> int:
    for i, rain in enumerate(reversed(daily_precip_mm)):
        if (rain or 0.0) >= threshold_mm:
            return i
    return len(daily_precip_mm)

def fuel_dryness(kbdi: float, recent_rain_mm: float, fuel: str) -> float:
    """
    0-1 dryness for fuel type
    blends drought signal the kbdi and recent rain and weighs how quickly that fuel dries.
    """

    tau = FUEL_REPONSE_TAU.get(fuel, 7.0)
    fast = math.exp(-recent_rain_mm/ (tau * 0.8))
    slow = kbdi / 800.0

    return round(min(1.0, 0.6 * fast + 0.4 * slow), 2)

def detect_windshift(hourly, now_idx: int, current_direction: float, horizon_h: int = 6):
    directions = hourly["wind_direction_10m"]

    for h in range(1, horizon_h + 1):
        idx = now_idx + h
        if idx >= len(directions):
            break
        flank_dir = directions[idx]
        if flank_dir is None:
            continue

        delta = abs((flank_dir - current_direction + 180) % 360 - 180)
        if delta >= 30:
            return{
                "in_hours": h,
                "from_deg": current_direction,
                "to_deg": flank_dir,
                "delta_deg": round(delta, 0),
                "message":(
                    f"Wind shifts {delta:.0f} degrees in {h}h ({compass(current_direction)} to {compass(flank_dir)})."
                    f"The {compass((current_direction + 90) % 360)} becomes the new head"
                )
            }
    return None

def get_fuel_conditions(lat: float, lng: float) -> dict:
    """
    Open-meteo call for the current conditions, 31 days of history of dryness and 2 day ahead wind forecast
    """

    params = {
        "latitude": lat,
        "longitude": lng,
        "current": [
            "temperature_2m", 
            "relative_humidity_2m",
            "wind_speed_10m", 
            "wind_direction_10m",
            "wind_gusts_10m"
        ],
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m", 
            "wind_direction_10m",
            "wind_gusts_10m"
        ],
        "daily": ["temperature_2m_max", "precipitation_sum"],
        "past_days": 31,
        "forecast_days": 2,
        "timezone": "Africa/Johannesburg"
    }
    try:
        resp = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        current = payload["current"]
        daily = payload["daily"]
        hourly = payload["hourly"]
    except (requests.RequestException, KeyError) as e:
        raise ValueError(f"Failed to fetch fuel conditions: {e}")

    precipitation_30 = [p or 0.0 for p in daily["precipitation_sum"][:31]]
    tmax_30 = [t if t is not None else 25.0 for t in daily["temperature_2m_max"][:31]]

    kbdi_series = compute_kbdi(precipitation_30, tmax_30)
    kbdi = kbdi_series[-1] if kbdi_series else 400.0
    recent_rain = sum(precipitation_30[-7:])

    fdi = lowveld_fdi(
        current["temperature_2m"],
        current["relative_humidity_2m"],
        current["wind_speed_10m"],
        kbdi
    )

    band, color = fdi_bands(fdi)

    now_idx = min(31 * 24, len(hourly["time"]) - 1)

    forecast = [
        {
            "time": hourly["time"][i],
            "temperature": hourly["temperature_2m"][i],
            "humidity": hourly["relative_humidity_2m"][i],
            "precipitation": hourly["precipitation"][i],
            "wind_speed": hourly["wind_speed_10m"][i],
            "wind_direction": hourly["wind_direction_10m"][i],
            "wind_gusts": hourly["wind_gusts_10m"][i],
        }
        for i in range(now_idx, min(now_idx + 7, len(hourly["time"])))
    ]

    last_rain = next((p for p in reversed(precipitation_30) if p >= 1.0), 0.0)

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "wind_direction": current["wind_direction_10m"],
        "wind_gusts": current["wind_gusts_10m"],
        "fdi": fdi,
        "fdi_band": band,
        "fdi_color": color,
        "kbdi": kbdi,
        "kbdi_series": kbdi_series,
        "days_since_rain": days_since_rain(precipitation_30),
        "rain_30d_mm": round(sum(precipitation_30), 1),
        "last_rain_mm": round(last_rain, 1),
        "dryness_grass": fuel_dryness(kbdi, recent_rain, "grass"),
        "dryness_shrub": fuel_dryness(kbdi, recent_rain, "shrub"),
        "dryness_plantation": fuel_dryness(kbdi, recent_rain, "plantation"),
        "forecast": forecast,
        "wind_shift": detect_windshift(hourly, now_idx, current["wind_direction_10m"]),
        "observed_at": current["time"],
        "source": "open-meteo"
    }