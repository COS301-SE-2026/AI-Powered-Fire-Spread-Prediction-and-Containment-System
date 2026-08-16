from __future__ import annotations
 
import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path
 
import numpy as np
import torch
from torch.utils.data import DataLoader, random_split
 
from app.ml.features.normalization import DeltaNormalizer, RawChannelNormalizer
from app.ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from app.ml.training.dataset import WeatherDatasetSplitConfig, WeatherRolloutDataset, attach_static_and_time, _hour_angle
from app.ml.training.losses import SmoothL1DeltaLoss
from app.ml.training.metrics import MetricTracker
 
@dataclass
class TrainConfig:
    weather_tensors_dir: str = "app/datasets/processed/weather_tensors"
    static_tensor_path: str = "app/datasets/processed/static/static_tensor.npz"
    input_hours: int = 6
    rollout_steps: int = 4
    hidden_dims: list[int] = field(default_factory=lambda: [48, 48])
    kernel_size: int = 3
    batch_size: int = 8
    epochs: int = 50
    lr: float = 1e-3
    weight_decay: float = 1e-4
    grad_clip_norm: float = 1.0
    tf_p_start: float = 1.0
    tf_p_end: float = 0.25
    tf_p_anneal_epochs: int = 50
    val_fraction: float = 0.15
    seed: int = 7
    device: str = "cuda" if torch.cuda.is_available() else "cpu"

def tf_p_for_epoch(epoch: int, cfg: TrainConfig) -> float:
    if cfg.tf_p_anneal_epochs <= 0:
        return cfg.tf_p_end
    frac = min(epoch / cfg.tf_p_anneal_epochs, 1.0)
    return cfg.tf_p_start + frac * (cfg.tf_p_end - cfg.tf_p_start)


class Trainer:
    def __init__(
        self,
        model: WeatherDeltaModel,
        train_loader: DataLoader,
        val_loader: DataLoader,
        static_tensor: np.ndarray,
        raw_normalizer: RawChannelNormalizer,
        delta_normalizer: DeltaNormalizer,
        cfg: TrainConfig,
    ):
        self.model = model.to(cfg.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.cfg = cfg
        self.device = cfg.device

        self.loss_fn = SmoothL1DeltaLoss()
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=cfg.epochs)

        self.static_tensor = torch.from_numpy(static_tensor.astype(np.float32)).to(self.device)

        delta_mean, delta_std = delta_normalizer.stats.mean, delta_normalizer.stats.std
        self.delta_mean = torch.from_numpy(delta_mean.astype(np.float32)).view(1, -1, 1, 1).to(self.device)
        self.delta_std = torch.from_numpy(delta_std.astype(np.float32)).view(1, -1, 1, 1).to(self.device)

        raw_mean, raw_std = raw_normalizer.stats.mean, raw_normalizer.stats.std
        self.raw_mean = torch.from_numpy(raw_mean.astype(np.float32)).view(1, -1, 1, 1).to(self.device)
        self.raw_std = torch.from_numpy(raw_std.astype(np.float32)).view(1, -1, 1, 1).to(self.device)

        self.best_val_loss = float("inf")

