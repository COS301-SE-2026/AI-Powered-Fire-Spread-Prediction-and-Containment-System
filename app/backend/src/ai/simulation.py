import torch
import numpy as np
from .ignition import IgnitionScorer
from .schema import UNBURNED, BURNING, BURNED 

# p_ignite is the output from the ignition scorer and is a 2D shape [H, W] and one probability per cell
# n_points is how many cells we want to turn into ignition points(sparks) the default is 1
# rng an optional random number generator that can be passed for a caller to control reproducibility, good for testing the simulation
# Return type is a boolean grid same shape as p_ignite, True where fire starts
# what is does: This function converts a continuous ignition-risk heatmap provided by the xgboost into a small number of discrete, randomly but probability weighted fire start points
# formated as a boolean grid that is expected by PyTorchFire
def pick_ignition_points(p_ignite: np.ndarray, n_points: int = 1, rng=None) -> np.ndarray: 
    rng = rng or np.random.default_rng()
    flat_p = p_ignite.ravel().astype(np.float64) # flattens the array into a 1D array

    if flat_p.sum() <= 0:
        raise ValueError("No ignition-prone cells: all P(ingite) are zero")
    flat_p /= flat_p.sum()

    idx = rng.choice(flat_p.size, size=n_points, replace=False, p=flat_p)

    mask = np.zeros(p_ignite.shape, dtype=bool)
    mask.flat[idx] = True # this is an iterator view over the 2D array, that maps the flattend postitions back onto the original 2D grid position
    return mask

def build_env_data(weather_np: dict, static_np: dict, initial_ignition_mask: np.ndarray) -> dict:

    u = torch.from_numpy(weather_np["wind_u"]).float()
    v = torch.from_numpy(weather_np["wind_v"]).float()

    wind_velocity = torch.sqrt(u**2 + v**2)
    wind_towards_direction = torch.rad2deg(torch.atan2(v,u)) % 360

    return {
        "p_veg": torch.from_numpy(static_np["fuel_load"]).float(),
        "p_den": torch.from_numpy(static_np["dryness"]).float(),
        "wind_velocity": wind_velocity,
        "wind_towards_direction": wind_towards_direction,
        "slope": torch.zeros((*wind_velocity.shape, 3, 3), dtype=torch.float32),
        "initial_ignition": torch.from_numpy(initial_ignition_mask).bool(),
    }