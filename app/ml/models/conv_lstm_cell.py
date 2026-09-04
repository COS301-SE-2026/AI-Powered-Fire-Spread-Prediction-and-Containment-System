from __future__ import annotations

import torch
import torch.nn as nn


class ConvLSTMCell(nn.Module):
    def __init__(
        self, input_dim: int, hidden_dim: int, kernel_size: int, bias: bool = True
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        padding = kernel_size // 2

        self.conv = nn.Conv2d(
            in_channels=input_dim + hidden_dim,
            out_channels=4 * hidden_dim,
            kernel_size=kernel_size,
            padding=padding,
            bias=bias,
        )

    def forward(
        self, x: torch.Tensor, cur_state: tuple[torch.Tensor, torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        h_cur, c_cur = cur_state
        combined = torch.cat([x, h_cur], dim=1)
        combined_conv = self.conv(combined)
        cc_i, cc_f, cc_o, cc_g = torch.split(combined_conv, self.hidden_dim, dim=1)

        i = torch.sigmoid(cc_i)
        f = torch.sigmoid(cc_f)
        o = torch.sigmoid(cc_o)
        g = torch.tanh(cc_g)

        c_next = f * c_cur + i * g
        h_next = o * torch.tanh(c_next)
        return h_next, c_next

    def init_hidden(
        self, batch_size: int, image_size: tuple[int, int]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        H, W = image_size
        device = self.conv.weight.device
        return (
            torch.zeros(batch_size, self.hidden_dim, H, W, device=device),
            torch.zeros(batch_size, self.hidden_dim, H, W, device=device),
        )