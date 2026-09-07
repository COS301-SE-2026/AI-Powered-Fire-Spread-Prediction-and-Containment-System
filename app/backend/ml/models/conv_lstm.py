from __future__ import annotations

import torch
import torch.nn as nn

from app.backend.ml.models.conv_lstm_cell import ConvLSTMCell


class ConvLSTM(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dims: list[int],
        kernel_size: int,
        num_layers: int | None = None,
        batch_first: bool = True,
        return_all_layers: bool = False,
    ):
        super().__init__()
        num_layers = num_layers or len(hidden_dims)
        if len(hidden_dims) != num_layers:
            raise ValueError("len(hidden_dims) must equal num_layers")

        self.num_layers = num_layers
        self.batch_first = batch_first
        self.return_all_layers = return_all_layers

        cells = []
        for i in range(num_layers):
            layer_input_dim = input_dim if i == 0 else hidden_dims[i - 1]
            cells.append(ConvLSTMCell(layer_input_dim, hidden_dims[i], kernel_size))
        self.cells = nn.ModuleList(cells)

    def forward(self, x: torch.Tensor, hidden_state: list[tuple] | None = None):
        if not self.batch_first:
            x = x.permute(1, 0, 2, 3, 4)
        B, T, _, H, W = x.shape

        if hidden_state is None:
            hidden_state = [cell.init_hidden(B, (H, W)) for cell in self.cells]

        layer_outputs = []
        last_states = []
        cur_input = x
        for layer_idx, cell in enumerate(self.cells):
            h, c = hidden_state[layer_idx]
            outputs = []
            for t in range(T):
                h, c = cell(cur_input[:, t], (h, c))
                outputs.append(h)
            layer_output = torch.stack(outputs, dim=1)
            cur_input = layer_output
            layer_outputs.append(layer_output)
            last_states.append((h, c))

        if not self.return_all_layers:
            layer_outputs = layer_outputs[-1:]
            last_states = last_states[-1:]

        return layer_outputs, last_states