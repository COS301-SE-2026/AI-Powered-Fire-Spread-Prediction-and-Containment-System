from __future__ import annotations

import numpy as np


class DeltaComputer:
    def compute_deltas(self, quarter_hourly_dynamic: np.ndarray) -> np.ndarray:
        if quarter_hourly_dynamic.shape[0] < 2:
            raise ValueError(
                "Input array must have at least 2 time steps to compute deltas."
            )
        return quarter_hourly_dynamic[1:] - quarter_hourly_dynamic[:-1]

    def reconstruct(self, anchor_frame: np.ndarray, deltas: np.ndarray) -> np.ndarray:
        cumulative = anchor_frame[None] + np.cumsum(deltas, axis=0)
        return np.concatenate([anchor_frame[None], cumulative], axis=0)