# Neighbour_features, grid_to_features
# Vectorized feature extraction: grid state to feature matrix

from __future__ import annotations

import numpy as np

from .schema import (FEATURES, WEATHER_FEATURES, STATIC_FEATURES, BURNING, DIST_CAP)

def shift(a: np.ndarray, dy: int, dx: int, fill=0) -> np.ndarray:
    """ Shifts 2D array. Cells shifted in from outside get `fill` """
    out = np.full_like(a, fill)
    h, w = a.shape
    ys_src = slice(max(0, -dy), min(h, h-dy))
    xs_src = slice(max(0, -dx), min(w, w-dx))
    ys_dst = slice(max(0, dy), min(h, h+dy))
    xs_dst = slice(max(0, dx), min(w, w+dx))
    out[ys_dst, xs_dst] = a[ys_src, xs_src]
    return out

# Moore neighbourhood offsets (dy, dx)
NEIGHBOURHOOD_OFFSETS = [(-1, -1), (-1, 0), (-1, 1),
                         (0, -1),           (0, 1),
                         (1, -1), (1, 0), (1, 1)]

def neighbour_features(burn_state: np.ndarray, wind_u: np.ndarray, wind_v: np.ndarray, elevation: np.ndarray) -> dict[str, np.ndarray]:
    """ Compute neighbour feature planes for a whole grid, vectorized """
    
    burning = (burn_state == BURNING).astype(np.float32)
    
    n_burning = np.zeros_like(burning)      # Count burning Moore neighbours
    for dy, dx in NEIGHBOURHOOD_OFFSETS:
        n_burning += shift(burning, dy, dx)
        
    # Upwind burning (is cell the wind blows from on fire?)
    sy = -np.sign(wind_v).astype(int)
    sx = -np.sign(wind_u).astype(int)
    upwind = np.zeros_like(burning)
    for dy, dx in NEIGHBOURHOOD_OFFSETS:
        mask = (sy == dy) & (sx == dx)
        if mask.any():
            upwind[mask] = shift(burning, -dy, -dx)[mask]
            
    # Downslope burning (burning neighbour at lower elevation)
    downslope = np.zeros_like(burning)
    for dy, dx in NEIGHBOURHOOD_OFFSETS:
        nb_burning = shift(burning, dy, dx)
        nb_elev = shift(elevation, dy, dx, fill=np.inf)
        downslope = np.maximum(downslope, nb_burning*(nb_elev < elevation))
        
    # Distance to nearest burning cell (capped)
    dist = np.full(burning.shape, DIST_CAP, dtype=np.float32)
    frontier = burning > 0
    dist[frontier] = 0.0
    reached = frontier.copy()
    for d in range(1, int(DIST_CAP)):
        grown = reached.copy()
        for dy, dx in NEIGHBOURHOOD_OFFSETS:
            grown |= shift(reached.astype(np.uint8), dy, dx).astype(bool)
        new = grown & ~reached
        dist[new] = d
        reached = grown
        if reached.all():
            break
        
    return{"n_burning_neighbours": n_burning, "upwind_burning": upwind, "downslope_burning": downslope, "dist_to_fire": dist,}

def grid_to_fmatrix(weather: dict[str, np.ndarray], static: dict[str, np.ndarray], burn_state: np.ndarray) -> np.ndarray:
    """ Assemble [H*W, len(FEATURES)] matrix for one tick. Column order exactly schema.FEATURES """
    
    nbf = neighbour_features(burn_state, weather["wind_u"], weather["wind_v"], static["elevation"])
    
    planes = []
    
    for name in FEATURES:
        if name in WEATHER_FEATURES:
            planes.append(weather[name])
        elif name in STATIC_FEATURES:
            planes.append(static[name])
        else:
            planes.append(nbf[name])
            
    return np.stack([p.ravel() for p in planes], axis=1).astype(np.float32)
    