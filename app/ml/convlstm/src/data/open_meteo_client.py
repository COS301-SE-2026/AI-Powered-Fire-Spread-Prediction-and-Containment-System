from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field

import requests

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_CHUNK_SIZE = 50
class OpenMeteoClient:
    base_url: str = ARCHIVE_URL
    timeout: int = 30
    session: requests.Session = field(default_factory=requests.Session)

    def fetch_hourly(
        self,
        lat: float,
        lon: float,
        variables: list[str],
        start_date: str,
        end_date: str,
    ) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(variables),
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "UTC",
    }
    return self._request_with_retry(params)
    def fetch_hourly_batch(
        self,
        coords: list[tuple[float, float]],
        variables: list[str],
        start_date: str,
        end_date: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> list[dict]:
        results: list[dict] = []
        for start in range(0, len(coords), chunk_size):
            chunk = coords[start : start + chunk_size]
            lats = ",".join(str(c[0]) for c in chunk)
            lons = ",".join(str(c[1]) for c in chunk)
            params = {
                "latitude": lats,
                "longitude": lons,
                "hourly": ",".join(variables),
                "start_date": start_date,
                "end_date": end_date,
                "timezone": "UTC",
            }
            response = self._request_with_retry(params)
            if isinstance(response, list):
                results.extend(response)
            else:
                results.append(response)
        return results
def _request_with_retry(self, params: dict, max_retries: int = 3) -> dict | list:
    last_exc: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = self.session.get(self.base_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            wait = 2 ** (attempt-1)
            logger.warning(
                "Open-Meteo request failed (attempt %d/%d): %s — retrying in %ds",
                attempt, max_retries, exc, wait,
            )
            time.sleep(wait)
        raise RuntimeError(f"Open-Meteo request failed after {max_retries} attempts") from last_exc
 