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
    
    

