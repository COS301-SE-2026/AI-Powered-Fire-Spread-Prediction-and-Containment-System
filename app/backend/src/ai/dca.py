import numpy as np
import torch
from pytorchfire import WildfireModel

from .ignition import IgnitionScorer
from .schema import UNBURNED
from .simulation import (
    build_env_data,
    build_verified_reports_mask,
    pick_ignition_points,
    state_to_burn_state,
)

MAXSTEPS = 144 # 2 ticks = 1 hour max ticks is 144 as 72 hours is max simulation time
TICK_MINUTES = 30 # how many minutes 1 tick is equivalent to


def run_dca(
    weather_grids: dict,
    static_grids: dict,
    cell_size_m: float,
    n_steps: int = 2,
    n_ignition_points: int = 1,
    ignition_points: list[tuple[int, int]] | None = None,
    ignition_mask: np.ndarray | None = None,
    params: dict | None = None,
):
    if n_steps > MAXSTEPS:
        raise ValueError(
            f"n_steps={n_steps} exceeds max steps:{MAXSTEPS}"
            f"({MAXSTEPS * TICK_MINUTES / 60:.0f} hours of simulated time)"
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"

    H, W = static_grids["elevation"].shape
    burn_state0 = np.full((H, W), UNBURNED, dtype=np.int64)

    if ignition_mask is not None:
        pass
    elif ignition_points:
        ignition_mask = build_verified_reports_mask(H, W, ignition_points)
    else:
        scorer = IgnitionScorer.load()
        p_ignite = scorer.score_grid(weather_grids, static_grids, burn_state0)
        ignition_mask = pick_ignition_points(p_ignite, n_points=n_ignition_points)

    env_data = build_env_data(weather_grids, static_grids, ignition_mask, cell_size_m)

    model = WildfireModel(env_data=env_data, params=params).to(device)
    model.eval()

    history = [state_to_burn_state(model.state)]

    with torch.no_grad():
        for _ in range(n_steps):
            model.compute()
            history.append(state_to_burn_state(model.state))

    return history
