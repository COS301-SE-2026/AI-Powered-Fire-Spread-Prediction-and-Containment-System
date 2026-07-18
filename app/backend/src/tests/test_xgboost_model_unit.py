import json
import numpy as np
import pytest 

from ai.schema import (FEATURES, WEATHER_FEATURES, STATIC_FEATURES, NEIGHBOUR_FEATURES, UNBURNED, BURNED, BURNING, DIST_CAP)
from ai.features import neighbour_features, grid_to_fmatrix, shift
from ai import artifact_store
from ai.ignition import IgnitionScorer
from training.synthetic_data import (generate_synthetic_dataset, SynthConfig, make_static, make_weathe)
from train.training_ignition import group_split, train

def test_schema_consistancy():
    assert FEATURES == WEATHER_FEATURES + STATIC_FEATURES + NEIGHBOUR_FEATURES
    assert len(FEATURES) == len(set(FEATURES)), "duplicate feature scheme"
    assert (UNBURNED, BURNING, BURNED) == (0, 1, 2)
    
def small_grids(H=5, W=5):
    """ Uniform weather blowing east, flat-ish terrain, no fire (example) """
    weather = {
        "wind_u": np.full((H, W), 3.0, np.float32),
        "wind_v": np.zeros((H,W), np.loat32),
        "rel_humidity": np.full((H,W), 30.0, np.float32),
        "temperature": np.full((H,W), 25.0, np.float32),
    }
    static = {
        "elevation": np.full((H,W), 500.0, np.float32),
        "slope": np.zeros((H,W), np.float32),
        "aspect_sin": np.zeros((H, W), np.float32),
        "aspect_cos": np.ones((H,W), np.float32),
        "fuel_load": np.full((H,W), 0.8, np.float32),
        "dryness": np.full((H,W), 0.6, np.float32),
    }
    burn = np.zeros((H,W), np.int8)
    return weather, static, burn


def test_shift_down():
    a = np.zeros((3, 3), np.float32)
    a[1, 1] = 1.0
    assert shift(a, 1, 0)[2, 1] == 1.0, "dy = +1 should shift content down"
    
def test_shift_down():
    a = np.zeros((3, 3), np.float32)
    a[1,1] = 1.0
    assert shift(a, 0, 1)[1, 2] == 1.0, "dx = +1 should shift content right"
    
def test_shift_diag():
    a = np.zeros((3, 3), np.float32)
    a[1,1] = 1.0
    assert shift(a, -1, -1)[0, 0] == 1.0, "dy = -1, dx = -1 should move content to top left"
    
def test_shift_fill():
    a = np.ones((3, 3), np.float32) 
    out = shift(a, 1, 0, fill=99)
    assert out[0, 0] == 99, "shifted-in cells should retrieve the fill value"
    
    
def test_neighbour_count_fire():
    """ All 8 Moore neighbours of fire cell see exactly 1 burning neighbour """
    weather, static, burn = small_grids()
    burn[2, 2] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    n = nbf["n_burning_neighbours"]
    assert n[1, 1] == n[1, 2] == n[1, 3] == 1
    assert n[2, 1] == n[2, 3] == 1
    assert n[3, 1] == n[3, 2] == n[3, 3] == 1
    
def test_neighbour_count_far_corner_zero():
    """ Cell far from fire should see zero burning neighbours """
    weather, static, burn = small_grids()
    burn[2, 2] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["n_burning_neighbours"][0, 0] == 0
    
def test_upwind_burning_east():
    """ Wind blows east. Cell east of fire has fire upwind (+u)"""
    weather, static, burn = small_grids()
    burn[2, 3] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["upwind_burning"][2, 3] == 1.0, "Cell east of fire should see it as upwind"
    
def test_upwind_burning_west_is_zero():
    """ Cell west of fire is upwind of it; so it should not see fire as upwind """
    weather, static, burn = small_grids()
    burn[2, 2] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["upwind_burning"][2, 1] == 0.0, "Cell west of fire is upwind of it"
    
def test_downslope_burning_lower_neighbour():
    """Cell uphill of burning cell should see downslope_burning = 1 """
    weather, static, burn = small_grids()
    static["elevation"][2, 2] = 400.0
    burn[2, 2] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["downslope_burning"][2, 3] == 1.0
    
def test_downslope_burning_highest_point_zero():
    """ If fire at highest point, no cell should see downslope_burning """
    weather, static, burn = small_grids()
    static["elevation"][2, 2] = 900.0
    burn[2, 2] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["downslope_burning"].sum() == 0
    
def test_dist_to_fire_at_fire():
    """ Distance at the fire cell itself should be 0 """
    weather, static, burn = small_grids(7, 7)
    burn[3, 3] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["dist_to_fire"][3, 3] == 0
    
def test_dist_to_fire_moore_diag():
    """ Moore neighbourhood: diag cell is distance 1, not 2 """
    weather, static, burn = small_grids(7, 7)
    burn[3, 3] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["dist_to_fire"][2, 2] == 1
    
def test_dist_to_fire_two_steps():
    """ Cell two steps away should be distance 2 """
    weather, static, burn = small_grids(7, 7)
    burn[3, 3] = BURNING
    nbf = neighbour_features(burn, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert nbf["dist_to_fire"][3, 5] == 2
    
def test_dist_to_fire_no_fire_caps():
    """ With no fire anywhere, all distances should equal DIST_CAP """
    weather, static, burn = small_grids(7, 7)
    nbf = neighbour_features(buen, weather["wind_u"], weather["wind_v"], static["elevation"])
    assert (nbf["dist_to_fire"] == DIST_CAP).all()
    
    
    
    

