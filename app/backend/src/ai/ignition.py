# IgnitionScorer (load_model, score_grid)
# Load once at process startup every tick (not at module import time in parent process)
# Inference runs on cpu deliberately (per-tick scoring is small matrix)

from __future__ import annotations

import json
import numpy as np
import xgboost as xgb

from . import artifact_store
from .features import grid_to_fmatrix
from .schema import FEATURES, SCHEMA_VERSION, UNBURNED


class IgnitionScorer:  # The only interface backend/simulation loop needs

    def __init__(self, booster: xgb.Booster, metadata: dict | None = None):
        self.booster = booster
        self.metadata = metadata or {}
        self.booster.set_param({"nthread": 2, "device": "cpu"})

    @classmethod
    def load(cls, version: str = "LATEST") -> "IgnitionScorer":
        """Load a published model from the artifact store by version name or current latest.
        Verifies training-time schema matches this code - guard that matters when models are trained on different machine than the one serving them
        """

        vdir = artifact_store.resolve("ignition", version)
        with open(vdir / "metadata.json") as f:
            metadata = json.load(f)

        if (
            metadata.get("features") != FEATURES
            or metadata.get("schema_version") != SCHEMA_VERSION
        ):
            raise RuntimeError(
                f"Schema mismatch: model '{metadata.get('version')}' was "
                f"trained with schema_version = {metadata.get('schema_version')} "
                f"features = {metadata.get('features')}, but this code has "
                f"schema_version={SCHEMA_VERSION}. Retrain / deploy the backend revision that matches the model"
            )

        booster = xgb.Booster()
        booster.load_model(str(vdir / "model.json"))
        return cls(booster, metadata)

    def score_grid(
        self,
        weather: dict[str, np.ndarray],
        static: dict[str, np.ndarray],
        burn_state: np.ndarray,
    ) -> np.ndarray:
        """weather: dict of [H,W] arrays, keys = schema.WEATHER_FEATURES
        static: dict of [H,W] arrays, keys = schema.STATIC_FEATURES
        burn_state: [H,W] ints in {UNBURNED, BURNING, BURNED}
        returns: [H,W] float32 P(ignite next tick), burning/burned = 0
        """
        H, W = burn_state.shape
        Xg = grid_to_fmatrix(weather, static, burn_state)
        p = self.booster.predict(xgb.DMatrix(Xg, feature_names=FEATURES))
        p = p.reshape(H, W).astype(np.float32)
        p[burn_state != UNBURNED] = 0.0

        return p
