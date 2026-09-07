from __future__ import annotations

import numpy as np

VARIABLES = ["wind_u", "wind_v", "relative_humidity", "temperature"]


class MetricTracker:
    def __init__(self, variables: list[str] = VARIABLES, num_steps: int = 4):
        self.variables = variables
        self.num_steps = num_steps
        self.reset()

    def reset(self) -> None:
        shape = (len(self.variables), self.num_steps)
        self._sq_err_model = np.zeros(shape, dtype=np.float64)
        self._sq_err_persistence = np.zeros(shape, dtype=np.float64)
        self._count = np.zeros(shape, dtype=np.int64)

    def update(
        self,
        pred_frames: np.ndarray,
        target_frames: np.ndarray,
        persistence_frames: np.ndarray,
    ) -> None:
        model_sq = (pred_frames - target_frames) ** 2
        persistence_sq = (persistence_frames - target_frames) ** 2
        for c in range(len(self.variables)):
            for s in range(self.num_steps):
                self._sq_err_model[c, s] += model_sq[:, s, c].sum()
                self._sq_err_persistence[c, s] += persistence_sq[:, s, c].sum()
                self._count[c, s] += model_sq[:, s, c].size

    def compute(self) -> dict:
        results: dict = {}
        for c, var in enumerate(self.variables):
            results[var] = {}
            for s in range(self.num_steps):
                n = max(self._count[c, s], 1)
                model_rmse = float(np.sqrt(self._sq_err_model[c, s] / n))
                persistence_rmse = float(np.sqrt(self._sq_err_persistence[c, s] / n))
                skill = (
                    1.0 - (model_rmse / persistence_rmse)
                    if persistence_rmse > 1e-8
                    else float("nan")
                )
                results[var][s + 1] = {
                    "model_rmse": model_rmse,
                    "persistence_rmse": persistence_rmse,
                    "skill": skill,
                }
        return results