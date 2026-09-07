from pydantic import BaseModel

class ForecastHour(BaseModel):
    time: str
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    wind_direction: float
    wind_gusts: float

class WindShift(BaseModel):
    in_hours: int
    from_deg: float
    to_deg: float
    delta_deg: float
    message: str

class FuelConditions(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    wind_gusts: float

    fdi: float
    fdi_band: str
    fdi_color: str

    kbdi: float
    kbdi_series: list[float]
    days_since_rain: int
    rain_30d_mm: float
    last_rain_mm: float

    dryness_grass: float
    dryness_shrub: float
    dryness_plantation: float

    forecast: list[ForecastHour]
    wind_shift: WindShift | None = None

    observed_at: str
    source: str = "open-meteo"
