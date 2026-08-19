import numpy as np
import torch

from .ignition import IgnitionScorer
from .schema import BURNED, BURNING, UNBURNED
from pytorchfire.utils import calculate_slope


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


def build_verified_reports_mask(
    H: int, W: int, ignition_points: list[tuple[int, int]]
) -> np.ndarray:
    mask = np.zeros((H, W), dtype=bool)

    for row, col in ignition_points:
        if 0 <= row < H and 0 <= col < W:
            mask[row, col] = True

    return mask

def build_boundary_ignition_mask(
        H: int, W: int, cell_size_m: float, boundary_radius_m: float
) -> np.ndarray:
    # marks every fire inside the boundary radius as ignited
    cy, cx = H / 2.0, W / 2.0
    radius_cells = boundary_radius_m / cell_size_m

    yy, xx = np.ogrid[0:H, 0:W]
    dist_cells = np.sqrt((yy - cy) **2 + (xx - cx) **2)

    return dist_cells <= radius_cells 


def compute_wind_components(
        wind_u: np.ndarray | torch.Tensor, 
        wind_v: np.ndarray | torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Converts u and v wind components into wind speed(m/s) and degrees to directions
    """

    u = torch.as_tensor(wind_u).float()
    v = torch.as_tensor(wind_v).float()
    
    wind_velocity = torch.sqrt(u**2 + v**2)

    # u - eastward & v - northward
    # 0 = East, 90 = North, 180 = West, 270 = South
    wind_towards_deg = (torch.rad2deg(torch.atan2(v, u))) % 360

    return wind_velocity, wind_towards_deg

def build_env_data(
    weather_grids: dict, static_grids: dict, initial_ignition_mask: np.ndarray, cell_size_m: float
) -> dict:

    wind_velocity, wind_towards_direction = compute_wind_components(
        weather_grids["wind_u"], weather_grids["wind_v"]
    )

    elevation = torch.from_numpy(static_grids["elevation"]).float()
    cell_size_t = torch.tensor(cell_size_m, dtype=torch.float32)

    slope = calculate_slope(elevation, torch.tensor(cell_size_m, dtype=torch.float32))

    env_dict = {
        "p_veg": torch.from_numpy(static_grids["fuel_load"]).float(),
        "p_den": torch.from_numpy(static_grids["dryness"]).float(),
        "wind_velocity": wind_velocity,
        "wind_towards_direction": wind_towards_direction,
        "slope": slope,
        "initial_ignition": torch.from_numpy(initial_ignition_mask).bool(),
    }

    return env_dict

def update_model_tensors(model, current_weather: dict, device: str | torch.device):
    """
    Updates the models weather during dca loop
    """

    velocity, direction = compute_wind_components(current_weather["wind_u"], current_weather["wind_v"])
    model.wind_velocity.copy_(velocity.to(device))
    model.wind_towards_direction.copy_(direction.to(device))

def state_to_burn_state(state: torch.Tensor) -> np.ndarray:
    # convert the Pytorchfire [2, H. W] bool state to schema.py's [H,W] int codes
    burning, burned = state.detach().cpu().numpy()
    burn_state_grid = np.full(burning.shape, UNBURNED, dtype=np.int64)
    burn_state_grid[burned] = BURNED
    burn_state_grid[burning] = BURNING
    return burn_state_grid
