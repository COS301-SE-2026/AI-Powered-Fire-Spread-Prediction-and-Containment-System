from __future__ import annotations

import numpy as np


class TemporalTargetBuilder:
    """
    Handles converting hourly dynamic data into smaller temporal steps.

    For example, if we have weather/fire data recorded every hour and
    substeps_per_hour = 4, this class can create data every 15 minutes
    using linear interpolation.
    """

    def __init__(self, substeps_per_hour: int = 4, method: str = "linear"):
        if method != "linear":
            raise NotImplementedError("Only linear interpolation is implemented.")
        self.substeps_per_hour = substeps_per_hour
        self.method = method

    def interpolate(self, hourly_dynamic: np.ndarray) -> np.ndarray:
        T, C, H, W = hourly_dynamic.shape
        if T < 2:
            raise ValueError(
                "Input array must have at least 2 time steps for interpolation."
            )
        n = self.substeps_per_hour
        out_len = (T - 1) * n + 1
        out = np.zeros((out_len, C, H, W), dtype=hourly_dynamic.dtype)
        for t in range(T - 1):
            start_frame = hourly_dynamic[t]
            end_frame = hourly_dynamic[t + 1]
            for i in range(n):
                weight = i / n
                out[t * n + i] = (1 - weight) * start_frame + weight * end_frame
        out[-1] = hourly_dynamic[-1]
        return out

    def build_naive_baseline(self, hourly_dynamic: np.ndarray) -> np.ndarray:
        return self.interpolate(hourly_dynamic)

    def quarter_hourly_timestamps(self, hourly_timestamps: list[str]) -> list[str]:
        from datetime import datetime, timedelta

        n = self.substeps_per_hour
        step_minutes = 60 // n
        out: list[str] = []
        parsed = [datetime.fromisoformat(ts) for ts in hourly_timestamps]
        for i in range(len(parsed) - 1):
            for k in range(n):
                out.append(
                    (parsed[i] + timedelta(minutes=step_minutes * k)).isoformat()
                )
        out.append(parsed[-1].isoformat())
        return out