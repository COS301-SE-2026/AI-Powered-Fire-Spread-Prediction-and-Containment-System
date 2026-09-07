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
    update_model_tensors
)

MAXSTEPS = 288 # 4 ticks = 1 hour max ticks is 288 as 72 hours is max simulation time
TICK_MINUTES = 15 # how many minutes 1 tick is equivalent to


def run_dca(
    weather_grids: dict,
    static_grids: dict,
    cell_size_m: float,
    n_steps: int = 4,
    n_ignition_points: int = 1,
    ignition_points: list[tuple[int, int]] | None = None,
    ignition_mask: np.ndarray | None = None,
    params: dict | None = None,
):
    """
    Executes the DCA to simulate fire spread

    Args:
        weather_grids: Static dict of weather rasters OR hourly list of weather states.
        static_grids: Environment rasters(elevation, slope, aspect, fuel load, dryness).
        cell_size_m: Physical resolution of each cell in meters(Used for spread speed scaling)
        n_steps: Number of ticks to run for
        n_ignition_points: Number of initial fires to seed if no coordinates are given
        ignition_points: The grid coordinates from a verified fire report
        ignition_mask: A optional 2d mask that indicates ignition locations
        params: The weightings for the CA spread and transition funcs

    Return:
        List of 2d integer numpy arrays that represent the burn state at each tick
        0 = UNBURNED
        1 = BURNING
        2 = BURNED
    """
    
    if n_steps > MAXSTEPS:
        raise ValueError(
            f"n_steps={n_steps} exceeds max steps:{MAXSTEPS}"
            f"({MAXSTEPS * TICK_MINUTES / 60:.0f} hours of simulated time)"
        )

    # Select the device to run the simulation on
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Get the spatial grid from the static rasters
    H, W = static_grids["elevation"].shape
    burn_state0 = np.full((H, W), UNBURNED, dtype=np.int64)

    # Use the first hours weather conidtions for initial setup
    init_weather = weather_grids[0] if isinstance(weather_grids, list) else weather_grids

    if ignition_mask is not None:
        pass
    elif ignition_points:
        ignition_mask = build_verified_reports_mask(H, W, ignition_points)
    else:
        scorer = IgnitionScorer.load()
        p_ignite = scorer.score_grid(init_weather, static_grids, burn_state0)
        ignition_mask = pick_ignition_points(p_ignite, n_points=n_ignition_points)

    # Pack environment raster and ignition locations into Tensors
    env_data = build_env_data(init_weather, static_grids, ignition_mask, cell_size_m)

    # Initialize the DCA model on device
    model = WildfireModel(env_data=env_data, params=params).to(device)
    model.eval()

    history = [state_to_burn_state(model.state)]

    # Run without the gradient tracking
    with torch.no_grad():
        for step in range(n_steps):
            if isinstance(weather_grids, list): # Updates weather tensors every 4 ticks if supplied with dynamic weather
                weather_idx = min(step // 4, len(weather_grids) - 1)
                update_model_tensors(model, weather_grids[weather_idx], device)

            model.compute()
            history.append(state_to_burn_state(model.state))

    return history
