export interface ForecastHour {
    time: string;
    temperature: number;
    humidity: number;
    precipitation: number;
    wind_speed: number;
    wind_direction: number;
    wind_gusts: number;
}

export interface WindShift {
    in_hours: number;
    from_deg: number;
    to_deg: number;
    delta_deg: number;
    message: string;
}

export interface FuelConditions {
    // current conditions
    temperature: number;
    humidity: number;
    wind_speed: number;
    wind_direction: number;
    wind_gusts: number;

    // Lowveld Fire Danger Index
    fdi: number;
    fdi_band: string;
    fdi_color: string;

    // 30-day dryness 
    kbdi: number;
    kbdi_series: number[];
    days_since_rain: number;
    rain_30d_mm: number;
    last_rain_mm: number;

    dryness_grass: number;
    dryness_shrub: number;
    dryness_plantation: number;

    forecast: ForecastHour[];
    wind_shift: WindShift | null;

    observed_at: string;
    source: string;
}