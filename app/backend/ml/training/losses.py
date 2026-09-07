"""
SmoothL1 used since it has been recommended by all research pretty much
It combines the convergence near zero of L2 (MSE, mean square error) with the robustness for outliers of L1 (MAE, mean average error)
"""

from __future__ import annotations

import torch
import torch.nn as nn


class SmoothL1DeltaLoss(nn.Module):
    def __init__(self, beta: float = 1.0):
        super().__init__()
        self.loss_fn = nn.SmoothL1Loss(beta=beta)

    def forward(
        self, pred_delta: torch.Tensor, target_delta: torch.Tensor
    ) -> torch.Tensor:
        return self.loss_fn(pred_delta, target_delta)