# Training and synthetic generator
# XGBoost ignition model training (run on either GPU)
# This script is self contained per machine. Pulls data, trains locally on GPU then publishes versioned artifact to shared store

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
import numpy as np
import xgboost as xgb

# Make backend_src importable when running from ml/
here = Path(__file__).resolve()
for cand in (here.parents[2] / "backend_src", here.parents[2]):
    if cand.is_dir() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))
        
from ai.schema import FEATURES, SCHEMA_VERSION
from ai import artifact_store
from training.synthetic_data import (generate_synthetic_dataset, SynthConfig)

# Load data
def load_dataset(source: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ source == "synthetic": placeholder data
        otherwise: path to .npz with arrays X, y, fire_ids (contract real data pipeline shout output)
    """
    if source == "synthetic":
        return generate_synthetic_dataset(SynthConfig())
    data = np.load(source)
    return data["X"], data["y"], data["fire_isds"]

def group_split(X, y, fire_ids, val_frac=0.2, seed=0):
    """ Split by fire event: all rows of a fire land on same side
        Random row splits leak badly here, rows from adjacent ticks of same fire nearly identical hence inflates validation scores
    """
    rng = np.random.default_rng(seed)
    fires = np.unique(fire_ids)
    rng.shuffle(fires)
    n_val = max(1, int(len(fires)*val_frac))
    val_fires = set(fires[:n_val].tolist())
    val_mask = np.isin(fire_ids, list(val_fires))
    return (X[~val_mask], y[~val_mask], X[val_mask], y[val_mask], sorted(val_fires))
