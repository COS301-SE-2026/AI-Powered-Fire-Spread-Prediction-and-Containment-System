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

from app.backend.src.ai.schema import FEATURES, SCHEMA_VERSION
from app.backend.src.ai import artifact_store
from app.backend.ml.training.synthetic_data import generate_synthetic_dataset, SynthConfig


# Load data
def load_dataset(source: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """source == "synthetic": placeholder data
    otherwise: path to .npz with arrays X, y, fire_ids (contract real data pipeline shout output)
    """
    if source == "synthetic":
        return generate_synthetic_dataset(SynthConfig())
    data = np.load(source)
    return data["X"], data["y"], data["fire_ids"]


# Ensures if a fire even is chosen for validation, every row associated with that fire goes to validation set
def group_split(X, y, fire_ids, val_frac=0.2, seed=0):
    """Split by fire event: all rows of a fire land on same side
    Random row splits leak badly here, rows from adjacent ticks of same fire nearly identical hence inflates validation scores
    """
    rng = np.random.default_rng(seed)
    fires = np.unique(fire_ids)
    rng.shuffle(fires)
    n_val = max(
        1, int(len(fires) * val_frac)
    )  # max(1,...) ensures at least 1 fire event placed in validation set
    val_fires = set(fires[:n_val].tolist())
    val_mask = np.isin(
        fire_ids, list(val_fires)
    )  # Checks fire_ids array, creates bool mask to check if each row's fire ID belongs to validation set
    return (
        X[~val_mask],
        y[~val_mask],
        X[val_mask],
        y[val_mask],
        sorted(val_fires),
    )  # '~' bitwise NOT, flips bools to pull training data (X[~val_mask], y[~val_mask]). Pulls out validation data (X[val_mask], y[val_mask])


# Training (Trains on XGBoost gradient boosting model) - optimised for imbalanced datasets
def train(X_train, y_train, X_va, y_va, device: str, seed: int = 0) -> xgb.Booster:
    pos = max(int(y_train.sum()), 1)
    neg = len(y_train) - pos
    spw = (
        neg / pos
    )  # spw = scale_pos_weight. Calculate ratio of negative examples to positive examples. spw val fed into xgboost config
    print(f"Train rows: {len(y_train):,} | val rows: {len(y_va):,} |")
    print(f"Positives: {100*y_train.mean():.2f}% |")
    print(f"Scale_pos_weight: {spw:.1f} | device: {device}")

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=FEATURES)
    dval = xgb.DMatrix(X_va, label=y_va, feature_names=FEATURES)

    # Config core behaviour of gradient booster
    params = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",  # aucpr = Area Under the Precision Recall Curve. How well model finds true positives without chucking out too many false alarms
        "tree_method": "hist",  # Histogram tree building because it's fast and allows shift to GPU if device="cuda"
        "device": device,
        "max_depth": 6,  # Prevent overfitting
        "eta": 0.08,  # Learning rate
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 4,
        "scale_pos_weight": spw,
        "seed": seed,
    }

    return xgb.train(
        params,
        dtrain,
        num_boost_round=600,
        evals=[(dtrain, "train"), (dval, "val")],
        early_stopping_rounds=40,
        verbose_eval=50,
    )


def main() -> None:
    # CLI
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--data",
        default="synthetic",
        help="'synthetic' or path to aligned .npz (X, y, fire_ids)",
    )
    ap.add_argument(
        "--device",
        default="cpu",
        help="cpu | cuda | cuda:0 (per machine: each host has 1 GPU)",
    )
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--promote",
        action="store_true",
        help="Point LATEST at this run after publishing",
    )
    args = ap.parse_args()

    # Execution pipeline
    X, y, fire_ids = load_dataset(args.data)
    X_train, y_train, X_va, y_va, val_fires = group_split(
        X, y, fire_ids, args.val_frac, args.seed
    )
    booster = train(X_train, y_train, X_va, y_va, args.device, args.seed)

    # Gain-based importance (Check against fire physics)
    imp = booster.get_score(importance_type="gain")
    print("Feature importance (gain):")

    for name, gain in sorted(imp.items(), key=lambda kv: -kv[1]):
        print(f"{name:22s} {gain:10.1f}")

    # Publish versioned artifact to shared store
    with tempfile.TemporaryDirectory() as td:
        model_path = Path(td) / "model.json"
        booster.save_model(str(model_path))
        version = artifact_store.publish(
            "ignition",
            model_path,
            metadata={
                "schema_version": SCHEMA_VERSION,
                "features": FEATURES,
                "data_source": args.data,
                "device": args.device,
                "seed": args.seed,
                "val_fires": [int(f) for f in val_fires],
                "best_iteration": int(booster.best_iteration),
                "val_aucpr": float(booster.best_score),
                "xgboost_version": xgb.__version__,
            },
            promote=args.promote,
        )
    print(
        f"Published: ignition/{version}"
        + (
            " (promoted to LATEST)"
            if args.promote
            else " (not promoted. Use artifact_store.promote_version to ship it)"
        )
    )


if __name__ == "__main__":
    main()
