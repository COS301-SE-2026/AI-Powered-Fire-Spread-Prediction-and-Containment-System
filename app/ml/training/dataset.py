from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import torch
from torch.utils.data import Dataset

from app.ml.features.normalization import DeltaNormalizer, RawChannelNormalizer


def _hour_angle(timestamps: list[str]) -> tuple[np.ndarray, np.ndarray]:
=    hours = np.array(
        [datetime.fromisoformat(ts).hour + datetime.fromisoformat(ts).minute / 60.0 for ts in timestamps],
        dtype=np.float32,
    )
    angle = 2 * np.pi * hours / 24.0
    return np.sin(angle).astype(np.float32), np.cos(angle).astype(np.float32)


def attach_static_and_time(
    dynamic: np.ndarray, static: np.ndarray, hour_sin: np.ndarray | float, hour_cos: np.ndarray | float
) -> np.ndarray:
    if dynamic.ndim == 3:
        _, H, W = dynamic.shape
        hs = np.full((1, H, W), hour_sin, dtype=np.float32)
        hc = np.full((1, H, W), hour_cos, dtype=np.float32)
        return np.concatenate([dynamic, static, hs, hc], axis=0)
    if dynamic.ndim == 4:
        T, _, H, W = dynamic.shape
        static_rep = np.broadcast_to(static, (T, 3, H, W))
        hs = np.asarray(hour_sin, dtype=np.float32).reshape(T, 1, 1, 1) * np.ones((1, 1, H, W), dtype=np.float32)
        hc = np.asarray(hour_cos, dtype=np.float32).reshape(T, 1, 1, 1) * np.ones((1, 1, H, W), dtype=np.float32)
        return np.concatenate([dynamic, static_rep, hs, hc], axis=1)
    raise ValueError(f"Unexpected dynamic tensor ndim {dynamic.ndim}")


@dataclass
class WeatherDatasetSplitConfig:
    input_hours: int = 6
    rollout_steps: int = 4


class WeatherRolloutDataset(Dataset):
    def __init__(
        self,
        npz_paths: list[str],
        static_tensor: np.ndarray,
        raw_normalizer: RawChannelNormalizer,
        delta_normalizer: DeltaNormalizer,
        cfg: WeatherDatasetSplitConfig = WeatherDatasetSplitConfig(),
    ):
        self.cfg = cfg
        self.static_tensor = static_tensor.astype(np.float32)
        self.raw_normalizer = raw_normalizer
        self.delta_normalizer = delta_normalizer

        self._hourly, self._hourly_ts, self._deltas = [], [], []
        for p in npz_paths:
            data = np.load(p)
            self._hourly.append(data["hourly_tensor"])
            self._hourly_ts.append(data["hourly_timestamps"])
            self._deltas.append(data["hourly_deltas"])

        self._index: list[tuple[int, int]] = []
        for file_idx, hourly in enumerate(self._hourly):
            T = hourly.shape[0]

            for h in range(cfg.input_hours - 1, T - 1 - cfg.rollout_steps + 1):
                self._index.append((file_idx, h))

    def __len__(self) -> int:
        return len(self._index)

    def __getitem__(self, idx: int) -> dict:
        file_idx, h = self._index[idx]
        cfg = self.cfg

        hourly = self._hourly[file_idx]
        hourly_ts = self._hourly_ts[file_idx]
        deltas = self._deltas[file_idx]

        window_dynamic = hourly[h - cfg.input_hours + 1 : h + 1]
        window_ts = [str(t) for t in hourly_ts[h - cfg.input_hours + 1 : h + 1]]
        w_sin, w_cos = _hour_angle(window_ts)
        input_seq = attach_static_and_time(window_dynamic, self.static_tensor, w_sin, w_cos)
        input_seq_norm = self._normalize_sequence(input_seq)

        anchor_dynamic_raw = hourly[h
        future_dynamic_raw = hourly[h + 1 : h + 1 + cfg.rollout_steps]
        future_ts = [str(t) for t in hourly_ts[h + 1 : h + 1 + cfg.rollout_steps]]
        future_hs, future_hc = _hour_angle(future_ts)

        future_deltas = deltas[h : h + cfg.rollout_steps]
        future_deltas_norm = self._normalize_deltas(future_deltas)

        return {
            "input_seq": torch.from_numpy(input_seq_norm.astype(np.float32)),
            "anchor_dynamic_raw": torch.from_numpy(anchor_dynamic_raw.astype(np.float32)),
            "future_dynamic_raw": torch.from_numpy(future_dynamic_raw.astype(np.float32)),
            "future_deltas_norm": torch.from_numpy(future_deltas_norm.astype(np.float32)),
            "future_hour_sin": torch.from_numpy(future_hs),
            "future_hour_cos": torch.from_numpy(future_hc),
        }

    def _normalize_sequence(self, seq: np.ndarray) -> np.ndarray:
        return np.stack([self.raw_normalizer.transform(frame) for frame in seq], axis=0)

    def _normalize_deltas(self, deltas: np.ndarray) -> np.ndarray:
        return np.stack([self.delta_normalizer.transform(frame) for frame in deltas], axis=0)