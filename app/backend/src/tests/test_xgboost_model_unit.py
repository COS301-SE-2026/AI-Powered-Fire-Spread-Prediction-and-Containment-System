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
    
