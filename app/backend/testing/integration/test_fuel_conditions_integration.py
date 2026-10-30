import json
import math
from unittest.mock import MagicMock, patch
import pytest
import requests

from app.backend.src.services.firefighter import fuel_conditions as fc
from app.backend.src.services.firefighter.fuel_conditions import (
    FDI_BANDS,
    FUEL_CONDITIONS_CACHE_TTL_SECONDS,
    FUEL_CONTITIONS_STALE_TTL_SECONDS,
    cache_get,
    cache_set,
    compass,
    compute_kbdi,
    days_since_rain,
    detect_windshift,
    fdi_bands,
    fetch_open_meteo,
    fuel_conditions_cache_key,
    fuel_dryness,
    get_fuel_conditions,
    lowveld_fdi,
)


@pytest.fixture
def fake_open_meteo_payload():
    now_hour = "2026-10-30T02:00"
    times = [f"2026-10-30T{h:02d}:00" for h in range(24)] + [f"2026-10-31T{h:02d}:00" for h in range(24)]
    return {
        "current": {
            "time": now_hour,
            "temperature_2m": 28.5,
            "relative_humidity_2m": 22.0,
            "wind_speed_10m": 18.0,
            "wind_direction_10m": 45.0,
            "wind_gusts_10m": 25.0,
        },
        "daily": {
            "temperature_2m_max": [30.0] * 31,
            "precipitation_sum": [0.0] * 25 + [3.0] + [0.0] * 5,
        },
        "hourly": {
            "time": times,
            "temperature_2m": [25.0] * len(times),
            "relative_humidity_2m": [30.0] * len(times),
            "precipitation": [0.0] * len(times),
            "wind_speed_10m": [15.0] * len(times),
            "wind_direction_10m": [45.0 + i * 2.0 for i in range(len(times))],
            "wind_gusts_10m": [20.0] * len(times),
        },
    }


class TestCacheIntegration:
    def test_cache_get_and_set_with_none_client(self, monkeypatch):
        monkeypatch.setattr(fc, "cache_client", None)
        assert cache_get("key1") is None
        assert cache_set("key1", {"a": 1}, 60) is None

    def test_cache_get_and_set_live_mock_client(self, monkeypatch):
        store = {}
        client = MagicMock()

        def mock_get(key):
            return store.get(key)

        def mock_set(key, val, ex=None):
            store[key] = val

        client.get.side_effect = mock_get
        client.set.side_effect = mock_set

        monkeypatch.setattr(fc, "cache_client", client)

        assert cache_get("missing_key") is None
        cache_set("test_key", {"status": "ok"}, 100)
        assert cache_get("test_key") == {"status": "ok"}

    def test_cache_swallows_client_exceptions(self, monkeypatch):
        client = MagicMock()
        client.get.side_effect = RuntimeError("Valkey read failure")
        client.set.side_effect = RuntimeError("Valkey write failure")
        monkeypatch.setattr(fc, "cache_client", client)

        assert cache_get("any_key") is None
        cache_set("any_key", {"data": 123}, 100)


class TestFetchOpenMeteoIntegration:
    @patch("requests.get")
    def test_fetch_open_meteo_success_first_attempt(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"hourly": {}}
        mock_get.return_value = mock_resp

        payload = fetch_open_meteo({"latitude": -25.7, "longitude": 28.2})
        assert payload == {"hourly": {}}
        assert mock_get.call_count == 1

    @patch("time.sleep", return_value=None)
    @patch("requests.get")
    def test_fetch_open_meteo_retries_on_503_and_recovers(self, mock_get, mock_sleep):
        resp_fail = MagicMock()
        resp_fail.status_code = 503

        resp_ok = MagicMock()
        resp_ok.status_code = 200
        resp_ok.json.return_value = {"recovered": True}

        mock_get.side_effect = [resp_fail, resp_ok]

        payload = fetch_open_meteo({"lat": 0}, attempts=2)
        assert payload == {"recovered": True}
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once()

    @patch("time.sleep", return_value=None)
    @patch("requests.get")
    def test_fetch_open_meteo_exhausts_retries_raises_http_error(self, mock_get, mock_sleep):
        resp_fail = MagicMock()
        resp_fail.status_code = 429
        mock_get.return_value = resp_fail

        with pytest.raises(requests.HTTPError):
            fetch_open_meteo({"lat": 0}, attempts=2)
        assert mock_get.call_count == 2

    @patch("time.sleep", return_value=None)
    @patch("requests.get")
    def test_fetch_open_meteo_connection_error_retry(self, mock_get, mock_sleep):
        mock_get.side_effect = requests.ConnectionError("Network down")

        with pytest.raises(requests.ConnectionError):
            fetch_open_meteo({"lat": 0}, attempts=2)
        assert mock_get.call_count == 2

    @patch("requests.get")
    def test_fetch_open_meteo_non_retryable_400_raises_immediately(self, mock_get):
        resp_400 = MagicMock()
        resp_400.status_code = 400
        resp_400.raise_for_status.side_effect = requests.HTTPError("Bad Request")
        mock_get.return_value = resp_400

        with pytest.raises(requests.HTTPError):
            fetch_open_meteo({"lat": 0}, attempts=3)
        assert mock_get.call_count == 1


class TestMeteorologicalCalculations:
    def test_compass_cardinal_and_boundary_bearings(self):
        assert compass(0) == "N"
        assert compass(90) == "E"
        assert compass(180) == "S"
        assert compass(270) == "W"
        assert compass(337.5) == "NNW"
        assert compass(350.0) == "N"

    def test_compute_kbdi_rainfall_and_bounds(self):
        precip = [None, 0.0, 10.0, 25.0]
        tmax = [None, 35.0, 32.0, 28.0]

        series = compute_kbdi(precip, tmax, annual_rain_mm=600.0, start=790.0)
        assert len(series) == 4
        assert all(0.0 <= val <= 800.0 for val in series)

    def test_lowveld_fdi_wind_speed_tiers(self):
        assert lowveld_fdi(30.0, 15.0, 4.0, 400.0) > 0.0
        assert lowveld_fdi(30.0, 15.0, 12.0, 400.0) > 0.0
        assert lowveld_fdi(30.0, 15.0, 20.0, 400.0) > 0.0
        assert lowveld_fdi(30.0, 15.0, 35.0, 400.0) > 0.0
        assert lowveld_fdi(30.0, 15.0, 55.0, 400.0) > 0.0

    def test_fdi_bands_all_categories(self):
        assert fdi_bands(20.0) == ("LOW", "blue")
        assert fdi_bands(50.0) == ("MODERATE", "green")
        assert fdi_bands(70.0) == ("DANGEROUS", "yellow")
        assert fdi_bands(85.0) == ("VERY DANGEROUS", "orange")
        assert fdi_bands(95.0) == ("EXTREMELY DANGEROUS", "red")
        assert fdi_bands(150.0) == ("EXTREMELY DANGEROUS", "red")

    def test_days_since_rain_logic(self):
        assert days_since_rain([0.0, 0.0, 2.5]) == 0
        assert days_since_rain([2.5, 0.0, 0.0]) == 2
        assert days_since_rain([0.0, 0.0, 0.0]) == 3

    def test_fuel_dryness_different_fuel_types(self):
        dry_grass = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="grass")
        dry_shrub = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="shrub")
        dry_plantation = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="plantation")
        dry_unknown = fuel_dryness(kbdi=500.0, recent_rain_mm=0.0, fuel="fynbos")

        assert 0.0 <= dry_grass <= 1.0
        assert 0.0 <= dry_shrub <= 1.0
        assert 0.0 <= dry_plantation <= 1.0
        assert 0.0 <= dry_unknown <= 1.0

    def test_detect_windshift_detected_and_not_detected(self):
        hourly_shift = {
            "wind_direction_10m": [0.0, None, 10.0, 80.0, 90.0]
        }
        shift = detect_windshift(hourly_shift, now_idx=0, current_direction=0.0, horizon_h=4)
        assert shift is not None
        assert shift["in_hours"] == 3
        assert shift["to_deg"] == 80.0
        assert "Wind shifts" in shift["message"]

        hourly_no_shift = {
            "wind_direction_10m": [10.0, 12.0, 15.0, 18.0]
        }
        assert detect_windshift(hourly_no_shift, now_idx=0, current_direction=10.0, horizon_h=3) is None

        short_hourly = {"wind_direction_10m": [0.0]}
        assert detect_windshift(short_hourly, now_idx=0, current_direction=0.0, horizon_h=5) is None


class TestGetFuelConditionsIntegrationWorkflow:
    def test_get_fuel_conditions_cache_hit(self):
        cached_val = {"fdi": 45.0, "status": "cached"}
        with patch("app.backend.src.services.firefighter.fuel_conditions.cache_get", return_value=cached_val):
            res = get_fuel_conditions(-25.74, 28.22)
            assert res == cached_val

    def test_get_fuel_conditions_end_to_end_success(self, fake_open_meteo_payload):
        client = MagicMock()
        stored_cache = {}

        def mock_get(key):
            return stored_cache.get(key)

        def mock_set(key, val, ex=None):
            stored_cache[key] = val

        client.get.side_effect = mock_get
        client.set.side_effect = mock_set

        with patch.object(fc, "cache_client", client), \
             patch("app.backend.src.services.firefighter.fuel_conditions.fetch_open_meteo", return_value=fake_open_meteo_payload):
            data = get_fuel_conditions(-25.74, 28.22)

            assert data["source"] == "open-meteo"
            assert "fdi" in data
            assert "fdi_band" in data
            assert "kbdi" in data
            assert len(data["forecast"]) <= 7
            assert len(stored_cache) == 2

            cached_res = get_fuel_conditions(-25.74, 28.22)
            assert cached_res["source"] == "open-meteo"

    def test_get_fuel_conditions_error_serves_stale_cache(self):
        stale_data = {"fdi": 60.0, "source": "open-meteo-stale"}

        def mock_cache_get(key):
            if key.endswith(":stale"):
                return stale_data
            return None

        with patch("app.backend.src.services.firefighter.fuel_conditions.cache_get", side_effect=mock_cache_get), \
             patch("app.backend.src.services.firefighter.fuel_conditions.fetch_open_meteo", side_effect=requests.RequestException("API error")):
            result = get_fuel_conditions(-25.74, 28.22)
            assert result["stale"] is True
            assert result["fdi"] == 60.0

    def test_get_fuel_conditions_error_no_stale_cache_raises_value_error(self):
        with patch("app.backend.src.services.firefighter.fuel_conditions.cache_get", return_value=None), \
             patch("app.backend.src.services.firefighter.fuel_conditions.fetch_open_meteo", side_effect=requests.RequestException("Connection refused")):
            with pytest.raises(ValueError, match="Weather provider is temporarily unavailiable"):
                get_fuel_conditions(-25.74, 28.22)

    def test_fuel_conditions_cache_key_formatting(self):
        key = fuel_conditions_cache_key(-25.74123, 28.2289)
        assert key == "weather:fuel-conditions:-25.74:28.23"