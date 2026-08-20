import logging
from pathlib import Path

import numpy as np
import torch

from ml.features.temporal_targets import TemporalTargetBuilder
from ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from ml.training.train_convlstm import build_normalizers

logger = logging.getLogger(__name__)

class WeatherForecastBridge:
    def __init__(self, artifact_dir: str = "app/artifact_store/weather_convlstm/LATEST")-> None:
        self.artifact_dir = Path(artifact_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model =None
        self.raw_norm = None
        self.delta_norm = None
        self.static_tensor = None
        self._initialize_model()

    @classmethod
    def load(cls, version: str = "LATEST") -> "WeatherForecastBridge":
        path = f"app/artifact_store/weather_convlstm/{version}"
        return cls(artifact_dir=path)

    def _initialize_model(self)-> None:
        static_path = Path("app/datasets/processed/static/static_tensor.npz")
        if not static_path.exists():
            logger.error("Static tensor missing at %s", static_path)
            raise FileNotFoundError(f"Static tensor missing at {static_path}. Run build_static_dataset first.")
        self.static_tensor = np.load(static_path)["static_tensor"]
        npz_paths = sorted(
            str(p) for p in Path("app/datasets/processed/weather_tensors").glob("weather_tensors_*.npz")
        )
        if not npz_paths.exists():
            logger.error("No processed weather tensors found for normalizer fitting.")
            raise FileNotFoundError("No processed weather tensors found for normalizer fitting.")
            