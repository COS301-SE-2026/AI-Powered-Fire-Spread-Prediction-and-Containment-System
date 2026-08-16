"""
boundary box and edge touch detection so if the DCA hits the edge but still needs to spread
"""

import math
import numpy as np

METERS_PER_DEG_LAT = 111320.0 # the amount of meters that 1 latitude on earth is equal to

def bbox_from_fire(
        lat: float,
        lng: float,
        boundary_radius_m: float,
        n_steps: int,
        max_spread_m_per_tick: float = 15.0, # placeholder will be changed after training/calibration
        min_pad_ratio: float = 2.0, # cannot pad less than 2 times the size of the reported fire
        min_extent_radius_m: float = 300
) -> tuple[float, float, float, float]: # (min_lon, min_lat, max_lon, max_lat)
    """ 
    Centers the boundary box around a fire and pads it beyond the reported size/radius of the fire
    """

    spread_headroom_m = n_steps * max_spread_m_per_tick

    padded_radius_m = max(
        boundary_radius_m * min_pad_ratio,
        boundary_radius_m + spread_headroom_m,
        min_extent_radius_m
    )

    m_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(lat))

    dlat = padded_radius_m / METERS_PER_DEG_LAT
    dlon = padded_radius_m / m_per_deg_lon

    return (lng - dlon, lat - dlat, lng + dlon, lat + dlat)

# signals if the simulation completed it spread of not if true it touched the edge and is not complete 
def touch_edge(
    burn_state_grid: np.ndarray, 
    burning_val: int, 
    burned_val: int
) -> bool:
    active = (burn_state_grid == burning_val) | (burn_state_grid == burned_val)

    if active.size == 0:
        return False

    return bool(
        active[0, :].any()
        or active[-1, :].any()
        or active[:, 0].any()
        or active[:, -1].any()
    )

