from __future__ import annotations

from dataclasses import dataclass, field

import torch
import torch.nn as nn

from app.ml.models.conv_lstm import ConvLSTM


@dataclass
class WeatherDeltaModelConfig:
    input_dim: int = 10
    hidden_dims: list[int] = field(default_factory=lambda: [48, 48])
    kernel_size: int = 3
    output_dim: int = 4


class WeatherDeltaModel(nn.Module):
    def __init__(self, cfg: WeatherDeltaModelConfig = WeatherDeltaModelConfig()):
        super().__init__()
        self.cfg = cfg
        self.encoder = ConvLSTM(
            input_dim=cfg.input_dim,
            hidden_dims=cfg.hidden_dims,
            kernel_size=cfg.kernel_size,
            return_all_layers=False,
        )
        self.head = nn.Conv2d(cfg.hidden_dims[-1], cfg.output_dim, kernel_size=1)
        self._init_zero_head()

    def _init_zero_head(self) -> None:
        nn.init.zeros_(self.head.weight)
        if self.head.bias is not None:
            nn.init.zeros_(self.head.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        layer_outputs, last_states = self.encoder(x)
        h_last, _ = last_states[-1]
        delta = self.head(h_last)
        return delta