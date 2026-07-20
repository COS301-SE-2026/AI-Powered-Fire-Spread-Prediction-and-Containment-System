import numpy as np
import pytest

from ai.schema import FEATURES, SCHEMA_VERSION, BURNING, BURNED, UNBURNED
from ai import artifact_store
from ai.ignition import IgnitionScorer
from training.synthetic_data import (generate_synthetic_dataset, SynthConfig, make_static, make_weather)
from training.train_ignition import group_split, train

# Shared helper function
def small_grids(H=5, W=5):
    """ Uniform weather blowing east, flat terrain, no fire """
    weather = {
        "wind_u": np.full((H, W), 3.0, np.float32),
        "wind_v": np.zeros((H, W), np.float32)
    }