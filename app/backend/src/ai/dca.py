import numpy as np
import torch
from pytorchfire import WildfireModel

from .ignition import IgnitionScorer
from .schema import UNBURNED
from .simulation import build_env_data, pick_ignition_points, state_to_burn_state


def run_dca(
    weather_grids: dict,
    static_grids: dict,
    n_steps: int = 100,
    n_ignition_points: int = 1,
    params: dict | None = None,
):

    device = "cuda" if torch.cuda.is_available() else "cpu"

    H, W = static_grids["elevation"].shape
    burn_state0 = np.full((H, W), UNBURNED, dtype=np.int64)

    scorer = IgnitionScorer.load()
    p_ignite = scorer.score_grid(weather_grids, static_grids, burn_state0)
    ignition_mask = pick_ignition_points(p_ignite, n_points=n_ignition_points)
    env_data = build_env_data(weather_grids, static_grids, ignition_mask)

    model = WildfireModel(env_data=env_data, params=params).to(device)
    model.eval()

    history = [state_to_burn_state(model.state)]

    with torch.no_grad():
        for _ in range(n_steps):
            model.compute()
            history.append(state_to_burn_state(model.state))

    return history
