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
