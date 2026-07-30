import numpy as np
import torch

from .ignition import IgnitionScorer
from .schema import UNBURNED, BURNING, BURNED


# p_ignite is the output from the ignition scorer and is a 2D shape [H, W] and one probability per cell
# n_points is how many cells we want to turn into ignition points(sparks) the default is 1
# rng an optional random number generator that can be passed for a caller to control reproducibility, good for testing the simulation
# Return type is a boolean grid same shape as p_ignite, True where fire starts
def pick_ignition_points(
    p_ignite: np.ndarray, n_points: int = 1, rng=None
) -> np.ndarray:
    rng = rng or np.random.default_rng()
    flat_p = p_ignite.ravel().astype(np.float64)  # flattens the array into a 1D array

    if flat_p.sum() <= 0:
        raise ValueError("No ignition-prone cells: all P(ingite) are zero")
    flat_p /= flat_p.sum()

    idx = rng.choice(flat_p.size, size=n_points, replace=False, p=flat_p)

    mask = np.zeros(p_ignite.shape, dtype=bool)
    mask.flat[idx] = (
        True  # this is an iterator view over the 2D array, that maps the flattend postitions back onto the original 2D grid position
    )
    return mask


def build_env_data(
    weather_grids: dict, static_grids: dict, initial_ignition_mask: np.ndarray
) -> dict:

    wind_u_comp = torch.from_numpy(weather_grids["wind_u"]).float()
    wind_v_comp = torch.from_numpy(weather_grids["wind_v"]).float()

    wind_velocity = torch.sqrt(wind_u_comp**2 + wind_v_comp**2)
    wind_towards_direction = torch.rad2deg(torch.atan2(wind_v_comp, wind_u_comp)) % 360

    return {
        "p_veg": torch.from_numpy(static_grids["fuel_load"]).float(),
        "p_den": torch.from_numpy(static_grids["dryness"]).float(),
        "wind_velocity": wind_velocity,
        "wind_towards_direction": wind_towards_direction,
        "slope": torch.zeros((*wind_velocity.shape, 3, 3), dtype=torch.float32),
        "initial_ignition": torch.from_numpy(initial_ignition_mask).bool(),
    }


def state_to_burn_state(state: torch.Tensor) -> np.ndarray:
    # convert the Pytorchfire [2, H. W] bool state to schema.py's [H,W] int codes
    burning, burned = state.detach().cpu().numpy()
    burn_state_grid = np.full(burning.shape, UNBURNED, dtype=np.int64)
    burn_state_grid[burning] = BURNING
    burn_state_grid[burned] = BURNED
    return burn_state_grid
