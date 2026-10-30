import json
from unittest.mock import MagicMock
import pytest
import requests

from app.backend.src.services.firefighter import fuel_conditions
from app.backend.src.services.firefighter.fuel_conditions import (
    cache_get,
    cache_set,
    fetch_open_meteo,
    fuel_conditions_cache_key,
    compass,
    compute_kbdi,
    lowveld_fdi,
    fdi_bands,
    days_since_rain,
    fuel_dryness,
    detect_windshift,
    get_fuel_conditions,
)


class TestCacheHelpers:
    def test_cache_get_client_none(self, monkeypatch):
        monkeypatch.setattr(fuel_conditions, "cache_client", None)
        assert cache_get("test:key") is None

    def test_cache_get_success(self, monkeypatch):
        mock_client = MagicMock()
        mock_client.get.return_value = json.dumps({"status": "ok"})
        monkeypatch.setattr(fuel_conditions, "cache_client", mock_client)
        assert cache_get("test:key") == {"status": "ok"}

    def test_cache_get_empty_or_none_value(self, monkeypatch):
        mock_client = MagicMock()
        mock_client.get.return_value = None
        monkeypatch.setattr(fuel_conditions, "cache_client", mock_client)
        assert cache_get("test:key") is None

    def test_cache_get_exception_returns_none(self, monkeypatch):
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Redis error")
        monkeypatch.setattr(fuel_conditions, "cache_client", mock_client)
        assert cache_get("test:key") is None

    def test_cache_set_client_none(self, monkeypatch):
        monkeypatch.setattr(fuel_conditions, "cache_client", None)
        assert cache_set("test:key", {"status": "ok"}, 60) is None

    def test_cache_set_success(self, monkeypatch):
        mock_client = MagicMock()
        monkeypatch.setattr(fuel_conditions, "cache_client", mock_client)
        cache_set("test:key", {"status": "ok"}, 60)
        mock_client.set.assert_called_once_with("test:key", json.dumps({"status": "ok"}), ex=60)

    def test_cache_set_exception_handled_silently(self, monkeypatch):
        mock_client = MagicMock()
        mock_client.set.side_effect = Exception("Write error")
        monkeypatch.setattr(fuel_conditions, "cache_client", mock_client)
        cache_set("test:key", {"status": "ok"}, 60)


class TestFetchOpenMeteo:
    def test_fetch_success_on_first_try(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"temperature": 25.0}
        monkeypatch.setattr(requests, "get", MagicMock(return_value=mock_resp))

        data = fetch_open_meteo({"lat": 1.0, "lng": 2.0}, attempts=2)
        assert data == {"temperature": 25.0}

    def test_fetch_retryable_status_exhausted_raises_http_error(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        monkeypatch.setattr(requests, "get", MagicMock(return_value=mock_resp))
        monkeypatch.setattr(fuel_conditions.time, "sleep", lambda _s: None)

        with pytest.raises(requests.HTTPError, match="open-meteo returned 503"):
            fetch_open_meteo({"lat": 1.0, "lng": 2.0}, attempts=2)

    def test_fetch_non_retryable_status_raises_immediately(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        monkeypatch.setattr(requests, "get", MagicMock(return_value=mock_resp))

        with pytest.raises(requests.HTTPError, match="Bad Request"):
            fetch_open_meteo({"lat": 1.0, "lng": 2.0}, attempts=3)

    def test_fetch_network_timeout_retries_and_raises(self, monkeypatch):
        monkeypatch.setattr(requests, "get", MagicMock(side_effect=requests.Timeout("Timeout")))
        monkeypatch.setattr(fuel_conditions.time, "sleep", lambda _s: None)

        with pytest.raises(requests.Timeout):
            fetch_open_meteo({"lat": 1.0, "lng": 2.0}, attempts=2)


class TestCalculationsAndBands:
    def test_fuel_conditions_cache_key(self):
        assert fuel_conditions_cache_key(-33.9249, 18.4241) == "weather:fuel-conditions:-33.92:18.42"

    def test_compass(self):
        assert compass(0) == "N"
        assert compass(90) == "E"
        assert compass(180) == "S"
        assert compass(270) == "W"
        assert compass(337.5) == "NNW"

    def test_compute_kbdi_with_missing_values_and_rainfall(self):
        precip = [None, 10.0, 0.0]
        tempmax = [None, 30.0, 35.0]
        series = compute_kbdi(precip, tempmax, annual_rain_mm=650.0, start=400.0)
        assert len(series) == 3
        assert all(isinstance(v, float) for v in series)

    def test_lowveld_fdi_wind_tiers(self):
        fdi_5 = lowveld_fdi(30.0, 20.0, 5.0, 400.0)
        fdi_15 = lowveld_fdi(30.0, 20.0, 15.0, 400.0)
        fdi_25 = lowveld_fdi(30.0, 20.0, 25.0, 400.0)
        fdi_40 = lowveld_fdi(30.0, 20.0, 40.0, 400.0)
        fdi_50 = lowveld_fdi(30.0, 20.0, 50.0, 400.0)

        assert fdi_5 < fdi_15 < fdi_25 < fdi_40 < fdi_50

    def test_fdi_bands(self):
        assert fdi_bands(20.0) == ("LOW", "blue")
        assert fdi_bands(50.0) == ("MODERATE", "green")
        assert fdi_bands(70.0) == ("DANGEROUS", "yellow")
        assert fdi_bands(85.0) == ("VERY DANGEROUS", "orange")
        assert fdi_bands(95.0) == ("EXTREMELY DANGEROUS", "red")
        assert fdi_bands(105.0) == ("EXTREMELY DANGEROUS", "red")

    def test_days_since_rain(self):
        assert days_since_rain([0.0, 2.0, 0.0]) == 1
        assert days_since_rain([0.0, 0.0, 3.0]) == 0
        assert days_since_rain([0.0, 0.5, 0.2]) == 3

    def test_fuel_dryness(self):
        dry_grass = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="grass")
        dry_shrub = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="shrub")
        dry_plantation = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="plantation")
        dry_custom = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="unknown_forest")

        assert 0.0 <= dry_grass <= 1.0
        assert 0.0 <= dry_shrub <= 1.0
        assert 0.0 <= dry_plantation <= 1.0
        assert 0.0 <= dry_custom <= 1.0


class TestDetectWindshift:
    def test_detect_windshift_success(self):
        hourly = {"wind_direction_10m": [10.0, 15.0, 60.0, 70.0]}
        shift = detect_windshift(hourly, now_idx=0, current_direction=10.0, horizon_h=3)
        assert shift is not None
        assert shift["in_hours"] == 2
        assert shift["from_deg"] == 10.0
        assert shift["to_deg"] == 60.0
        assert shift["delta_deg"] == 50.0

    def test_detect_windshift_skips_none_and_breaks_at_end(self):
        hourly = {"wind_direction_10m": [10.0, None]}
        shift = detect_windshift(hourly, now_idx=0, current_direction=10.0, horizon_h=4)
        assert shift is None

    def test_detect_windshift_no_significant_shift(self):
        hourly = {"wind_direction_10m": [10.0, 12.0, 15.0, 18.0]}
        shift = detect_windshift(hourly, now_idx=0, current_direction=10.0, horizon_h=3)
        assert shift is None


class TestGetFuelConditions:
    def test_get_fuel_conditions_cache_hit(self, monkeypatch):
        mock_payload = {"temperature": 22.0, "source": "open-meteo"}
        monkeypatch.setattr(fuel_conditions, "cache_get", lambda _k: mock_payload)
        res = get_fuel_conditions(-33.9, 18.4)
        assert res == mock_payload

    def test_get_fuel_conditions_provider_failure_with_stale_cache(self, monkeypatch):
        def mock_cache_get(k):
            if k.endswith(":stale"):
                return {"temperature": 20.0, "source": "open-meteo"}
            return None

        monkeypatch.setattr(fuel_conditions, "cache_get", mock_cache_get)
        monkeypatch.setattr(fuel_conditions, "fetch_open_meteo", MagicMock(side_effect=requests.ConnectionError("Failed")))

        res = get_fuel_conditions(-33.9, 18.4)
        assert res["temperature"] == 20.0
        assert res["stale"] is True

    def test_get_fuel_conditions_provider_failure_no_stale_raises_value_error(self, monkeypatch):
        monkeypatch.setattr(fuel_conditions, "cache_get", lambda _k: None)
        monkeypatch.setattr(fuel_conditions, "fetch_open_meteo", MagicMock(side_effect=requests.ConnectionError("Failed")))

        with pytest.raises(ValueError, match="Weather provider is temporarily unavailiable"):
            get_fuel_conditions(-33.9, 18.4)

    def test_get_fuel_conditions_success(self, monkeypatch):
        monkeypatch.setattr(fuel_conditions, "cache_get", lambda _k: None)
        set_calls = {}

        def mock_cache_set(k, v, ttl):
            set_calls[k] = v

        monkeypatch.setattr(fuel_conditions, "cache_set", mock_cache_set)

        fake_open_meteo_payload = {
            "current": {
                "time": "2026-06-01T12:00",
                "temperature_2m": 27.5,
                "relative_humidity_2m": 35.0,
                "wind_speed_10m": 18.0,
                "wind_direction_10m": 120.0,
                "wind_gusts_10m": 25.0,
            },
            "daily": {
                "precipitation_sum": [0.0] * 30 + [2.5],
                "temperature_2m_max": [28.0] * 31,
            },
            "hourly": {
                "time": [f"2026-06-01T{h:02d}:00" for h in range(24)],
                "temperature_2m": [25.0] * 24,
                "relative_humidity_2m": [40.0] * 24,
                "precipitation": [0.0] * 24,
                "wind_speed_10m": [15.0] * 24,
                "wind_direction_10m": [120.0] * 24,
                "wind_gusts_10m": [20.0] * 24,
            },
        }

        monkeypatch.setattr(fuel_conditions, "fetch_open_meteo", lambda _p: fake_open_meteo_payload)

        res = get_fuel_conditions(-33.92, 18.42)
        assert res["temperature"] == 27.5
        assert res["humidity"] == 35.0
        assert res["fdi_band"] in ["LOW", "MODERATE", "DANGEROUS", "VERY DANGEROUS", "EXTREMELY DANGEROUS"]
        assert len(res["forecast"]) <= 7
        assert "weather:fuel-conditions:-33.92:18.42" in set_calls