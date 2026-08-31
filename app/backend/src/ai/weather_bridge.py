import logging
from pathlib import Path

import numpy as np
import torch

from app.ml.features.temporal_targets import TemporalTargetBuilder
from app.ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from app.ml.training.train_convlstm import build_normalizers

logger = logging.getLogger(__name__)


class WeatherForecastBridge:
    def __init__(
        self, artifact_dir: str = "app/artifact_store/weather_convlstm/LATEST"
    ) -> None:
        self.artifact_dir = Path(artifact_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.raw_norm = None
        self.delta_norm = None
        self.static_tensor = None
        self._initialize_model()

    @classmethod
    def load(cls, version: str = "LATEST") -> "WeatherForecastBridge":
        path = f"app/artifact_store/weather_convlstm/{version}"
        return cls(artifact_dir=path)

    def _initialize_model(self) -> None:
        static_path = Path("app/datasets/processed/static/static_tensor.npz")
        if not static_path.exists():
            logger.error("Static tensor missing at %s", static_path)
            raise FileNotFoundError(
                f"Static tensor missing at {static_path}. Run build_static_dataset first."
            )
        self.static_tensor = np.load(static_path)["static_tensor"]
        if not hasattr(self, "raw_norm") or self.raw_norm is None:
            npz_paths = sorted(
                str(p)
                for p in Path("app/datasets/processed/weather_tensors").glob(
                    "weather_tensors_*.npz"
                )
                if p.name != "weather_tensors.npz" and p.stat().st_size > 0
            )
            if not npz_paths:
                logger.error(
                    "No processed weather tensors found for normalizer fitting."
                )
                raise FileNotFoundError(
                    "No processed weather tensors found for normalizer fitting."
                )

            # Slice to only the first available year to avoid loading all 18+ dataset files during init
            self.raw_norm, self.delta_norm = build_normalizers(
                npz_paths[:1], self.static_tensor
            )

        config = WeatherDeltaModelConfig(input_dim=10)
        self.model = WeatherDeltaModel(config)

        model_path = self.artifact_dir / "model.pt"
        if not model_path.exists():
            logger.error("Model checkpoint not found at %s", model_path)
            raise FileNotFoundError(f"Model checkpoint not found at {model_path}")

        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.to(self.device)
            self.model.eval()
        except Exception as exc:
            logger.error("Failed to load model weights: %s", exc)
            raise RuntimeError(
                f"Failed to initialize WeatherDeltaModel: {exc}"
            ) from exc

    def forecast_for_simulation(
        self,
        history_tensor: np.ndarray,
        rollout_steps: int = 4,
        substeps_per_hour: int = 4,
    ) -> np.ndarray:
        norm_history = self.raw_norm.transform(history_tensor)
        current_window = (
            torch.tensor(norm_history, dtype=torch.float32).unsqueeze(0).to(self.device)
        )

        preds_hourly = []

        with torch.no_grad():
            for _ in range(rollout_steps):
                pred_delta_norm = self.model(current_window)
                pred_delta = self.delta_norm.inverse_transform(
                    pred_delta_norm.cpu().numpy()[0]
                )

                last_frame = (
                    history_tensor[-1] if not preds_hourly else preds_hourly[-1]
                )
                next_frame = last_frame + pred_delta

                preds_hourly.append(next_frame)

                next_norm = self.raw_norm.transform(next_frame[np.newaxis, ...])
                next_tensor = (
                    torch.tensor(next_norm, dtype=torch.float32)
                    .unsqueeze(0)
                    .to(self.device)
                )
                current_window = torch.cat([current_window[:, 1:], next_tensor], dim=1)

        hourly_array = np.stack(preds_hourly, axis=0)

        interpolator = TemporalTargetBuilder(
            substeps_per_hour=substeps_per_hour, method="linear"
        )
        full_sequence = np.concatenate([history_tensor[-1:], hourly_array], axis=0)

        return interpolator.interpolate(full_sequence)
