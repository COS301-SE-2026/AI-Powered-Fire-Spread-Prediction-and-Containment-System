from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import torch
from torch.utils.data import Dataset

from app.backend.ml.features.normalization import DeltaNormalizer, RawChannelNormalizer


def _hour_angle(timestamps: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """this function take the ISO-formatted timestamp strings
    and converts them to cyclic time embeddings, meaning it allows the model to understand
    the cyclical nature of time, i.e. every day starts at the beginnign, so 23:00 and 01:00 are
    close to eachother, very cool"""
    hours = np.array(
        [
            datetime.fromisoformat(ts).hour + datetime.fromisoformat(ts).minute / 60.0
            for ts in timestamps
        ],
        dtype=np.float32,
    )
    angle = 2 * np.pi * hours / 24.0
    return np.sin(angle).astype(np.float32), np.cos(angle).astype(np.float32)


def attach_static_and_time(
    dynamic: np.ndarray,
    static: np.ndarray,
    hour_sin: np.ndarray | float,
    hour_cos: np.ndarray | float,
) -> np.ndarray:
    """
    takes the dynamic weather features and static terrain features, combines them into
    a big array, along with the cyclical time features
    """
    if dynamic.ndim == 3:
        _, H, W = dynamic.shape
        hs = np.full((1, H, W), hour_sin, dtype=np.float32)
        hc = np.full((1, H, W), hour_cos, dtype=np.float32)
        return np.concatenate([dynamic, static, hs, hc], axis=0)
    if dynamic.ndim == 4:
        T, _, H, W = dynamic.shape
        C_static = static.shape[0]
        static_rep = np.broadcast_to(static, (T, C_static, H, W))
        hs = np.asarray(hour_sin, dtype=np.float32).reshape(T, 1, 1, 1) * np.ones(
            (1, 1, H, W), dtype=np.float32
        )
        hc = np.asarray(hour_cos, dtype=np.float32).reshape(T, 1, 1, 1) * np.ones(
            (1, 1, H, W), dtype=np.float32
        )
        return np.concatenate([dynamic, static_rep, hs, hc], axis=1)
    raise ValueError(f"Unexpected dynamic tensor ndim {dynamic.ndim}")


@dataclass
class WeatherDatasetSplitConfig:
    input_hours: int = 6
    rollout_steps: int = 4


# This class handles the heavy lifting of slicing the data
# into valid training batches :)


class WeatherRolloutDataset(Dataset):
    def __init__(
        self,
        npz_paths: list[str],
        static_tensor: np.ndarray,
        raw_normalizer: RawChannelNormalizer,
        delta_normalizer: DeltaNormalizer,
        cfg: WeatherDatasetSplitConfig = WeatherDatasetSplitConfig(),
    ):
        """obv initializes class
        stores normalizers into static tensors, then loads hourly npz. arrays"""
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
        # get length
        return len(self._index)

    def __getitem__(self, idx: int) -> dict:
        # gets item at index
        file_idx, h = self._index[idx]
        cfg = self.cfg

        hourly = self._hourly[file_idx]
        hourly_ts = self._hourly_ts[file_idx]
        deltas = self._deltas[file_idx]

        window_dynamic = hourly[h - cfg.input_hours + 1 : h + 1]
        window_ts = [str(t) for t in hourly_ts[h - cfg.input_hours + 1 : h + 1]]
        w_sin, w_cos = _hour_angle(window_ts)
        input_seq = attach_static_and_time(
            window_dynamic, self.static_tensor, w_sin, w_cos
        )
        input_seq_norm = self._normalize_sequence(input_seq)

        anchor_dynamic_raw = hourly[h]
        future_dynamic_raw = hourly[h + 1 : h + 1 + cfg.rollout_steps]
        future_ts = [str(t) for t in hourly_ts[h + 1 : h + 1 + cfg.rollout_steps]]
        future_hs, future_hc = _hour_angle(future_ts)

        future_deltas = deltas[h : h + cfg.rollout_steps]
        future_deltas_norm = self._normalize_deltas(future_deltas)

        return {
            "input_seq": torch.from_numpy(input_seq_norm.astype(np.float32)),
            "anchor_dynamic_raw": torch.from_numpy(
                anchor_dynamic_raw.astype(np.float32)
            ),
            "future_dynamic_raw": torch.from_numpy(
                future_dynamic_raw.astype(np.float32)
            ),
            "future_deltas_norm": torch.from_numpy(
                future_deltas_norm.astype(np.float32)
            ),
            "future_hour_sin": torch.from_numpy(future_hs),
            "future_hour_cos": torch.from_numpy(future_hc),
        }

    def _normalize_sequence(self, seq: np.ndarray) -> np.ndarray:
        """helper that applies normalizer to a sequecnce of input frames"""
        return np.stack([self.raw_normalizer.transform(frame) for frame in seq], axis=0)

    def _normalize_deltas(self, deltas: np.ndarray) -> np.ndarray:
        """helper that applies the DeltaNormalizer to the target outputs"""
        return np.stack(
            [self.delta_normalizer.transform(frame) for frame in deltas], axis=0
        )

    def split_by_month(
        self, val_months: set[int]
    ) -> tuple["torch.utils.data.Subset", "torch.utils.data.Subset"]:
        """instead of random shuffle, this function splits the dataset into training and validation
        sets strictly by month"""
        from datetime import datetime as _dt

        from torch.utils.data import Subset

        train_idx, val_idx = [], []
        for i, (file_idx, h) in enumerate(self._index):
            anchor_ts = str(self._hourly_ts[file_idx][h])
            month = _dt.fromisoformat(anchor_ts).month
            (val_idx if month in val_months else train_idx).append(i)

        if not val_idx:
            raise ValueError(
                f"val_months={val_months} matched no samples — check the "
                "months actually present in the fetched data."
            )
        if not train_idx:
            raise ValueError(
                f"val_months={val_months} matched every sample — nothing left to train on."
            )

        return Subset(self, train_idx), Subset(self, val_idx)