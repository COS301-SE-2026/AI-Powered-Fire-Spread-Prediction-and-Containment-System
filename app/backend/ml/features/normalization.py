from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class _ChannelStats:
    mean: np.ndarray = field(default_factory=lambda: np.zeros(0, dtype=np.float64))
    std: np.ndarray = field(default_factory=lambda: np.ones(0, dtype=np.float64))

    def to_dict(self) -> dict:
        return {"mean": self.mean.tolist(), "std": self.std.tolist()}

    @classmethod
    def from_dict(cls, d: dict) -> "_ChannelStats":
        return cls(mean=np.array(d["mean"]), std=np.array(d["std"]))


class _BaseNormalizer:
    def __init__(self):
        self.stats = _ChannelStats()

    def fit(self, tensor: np.array) -> None:
        C = tensor.shape[-3]
        flat = np.moveaxis(tensor, -3, 0).reshape(C, -1)
        mean = flat.mean(axis=1)
        std = flat.std(axis=1)
        std = np.where(
            std < 1e-8, 1.0, std
        )  # 1e-8 is equivalent to zero sortof, but we avoid div by zero :)
        self.stats = _ChannelStats(mean=mean, std=std)

    def transform(self, tensor: np.ndarray) -> np.ndarray:
        mean = self.stats.mean.reshape(-1, 1, 1)
        std = self.stats.std.reshape(-1, 1, 1)
        return (tensor - mean) / std

    def inverse_transform(self, tensor: np.ndarray) -> np.ndarray:
        mean = self.stats.mean.reshape(-1, 1, 1)
        std = self.stats.std.reshape(-1, 1, 1)
        return tensor * std + mean

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.stats.to_dict()))

    def load(self, path: str) -> None:
        self.stats = _ChannelStats.from_dict(json.loads(Path(path).read_text()))


class RawChannelNormalizer(_BaseNormalizer):
    pass


class DeltaNormalizer(_BaseNormalizer):
    pass