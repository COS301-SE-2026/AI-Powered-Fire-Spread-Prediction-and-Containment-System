from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, random_split

from app.backend.ml.features.normalization import DeltaNormalizer, RawChannelNormalizer
from app.backend.ml.models.nowcast_model import WeatherDeltaModel, WeatherDeltaModelConfig
from app.backend.ml.training.dataset import (
    WeatherDatasetSplitConfig,
    WeatherRolloutDataset,
    attach_static_and_time,
    _hour_angle,
)
from app.backend.ml.training.losses import SmoothL1DeltaLoss
from app.backend.ml.training.metrics import MetricTracker


@dataclass
class TrainConfig:
    weather_tensors_dir: str = "app/datasets/processed/weather_tensors"
    static_tensor_path: str = "app/datasets/processed/static/static_tensor.npz"
    input_hours: int = 6
    rollout_steps: int = 4
    hidden_dims: list[int] = field(default_factory=lambda: [48, 48])
    kernel_size: int = 3
    batch_size: int = 8
    epochs: int = 50
    lr: float = 1e-3
    weight_decay: float = 1e-4
    grad_clip_norm: float = 1.0
    tf_p_start: float = 1.0
    tf_p_end: float = 0.25
    tf_p_anneal_epochs: int = 50
    val_fraction: float = 0.15
    seed: int = 7
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def tf_p_for_epoch(epoch: int, cfg: TrainConfig) -> float:
    """
    calculates "teacher forcing" probability ofr current epoch
    it linearly decays prob from tf_p_start to _tf_p_end over a set number of epochs
    """
    if cfg.tf_p_anneal_epochs <= 0:
        return cfg.tf_p_end
    frac = min(epoch / cfg.tf_p_anneal_epochs, 1.0)
    return cfg.tf_p_start + frac * (cfg.tf_p_end - cfg.tf_p_start)


class Trainer:
    """this encapsulates the whole training process for the model"""

    def __init__(
        self,
        model: WeatherDeltaModel,
        train_loader: DataLoader,
        val_loader: DataLoader,
        static_tensor: np.ndarray,
        raw_normalizer: RawChannelNormalizer,
        delta_normalizer: DeltaNormalizer,
        cfg: TrainConfig,
    ):
        """
        maps model to the gpu/cpu
        pre-loads static terrain and normalization stats for easy memory access
        """
        self.model = model.to(cfg.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.cfg = cfg
        self.device = cfg.device

        self.loss_fn = SmoothL1DeltaLoss()
        self.optimizer = torch.optim.AdamW(
            model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=cfg.epochs
        )

        self.static_tensor = torch.from_numpy(static_tensor.astype(np.float32)).to(
            self.device
        )

        delta_mean, delta_std = delta_normalizer.stats.mean, delta_normalizer.stats.std
        self.delta_mean = (
            torch.from_numpy(delta_mean.astype(np.float32))
            .view(1, -1, 1, 1)
            .to(self.device)
        )
        self.delta_std = (
            torch.from_numpy(delta_std.astype(np.float32))
            .view(1, -1, 1, 1)
            .to(self.device)
        )

        raw_mean, raw_std = raw_normalizer.stats.mean, raw_normalizer.stats.std
        self.raw_mean = (
            torch.from_numpy(raw_mean.astype(np.float32))
            .view(1, -1, 1, 1)
            .to(self.device)
        )
        self.raw_std = (
            torch.from_numpy(raw_std.astype(np.float32))
            .view(1, -1, 1, 1)
            .to(self.device)
        )

        self.best_val_loss = float("inf")

    def _attach_and_normalize(
        self, dynamic_raw: torch.Tensor, hour_sin: torch.Tensor, hour_cos: torch.Tensor
    ) -> torch.Tensor:
        """dynamic_raw: (B,4,H,W); hour_sin/hour_cos: (B,). Returns
        normalized (B,9,H,W) ready to append to the input window."""
        B, _, H, W = dynamic_raw.shape
        static_batch = self.static_tensor.unsqueeze(0).expand(B, -1, -1, -1)
        hs = hour_sin.view(B, 1, 1, 1).expand(-1, 1, H, W)
        hc = hour_cos.view(B, 1, 1, 1).expand(-1, 1, H, W)
        full_raw = torch.cat([dynamic_raw, static_batch, hs, hc], dim=1)  # (B,9,H,W)
        return (full_raw - self.raw_mean) / self.raw_std

    def _rollout(self, batch: dict, tf_p: float) -> dict:
        """
        steps through the multi-hour forecast window one step at a time.
        At each step, it predicts the next weather delta
        """
        window = batch["input_seq"].to(self.device)
        current_dynamic_raw = batch["anchor_dynamic_raw"].to(self.device)
        future_dynamic_raw = batch["future_dynamic_raw"].to(self.device)
        future_deltas_norm = batch["future_deltas_norm"].to(self.device)
        future_hour_sin = batch["future_hour_sin"].to(self.device)
        future_hour_cos = batch["future_hour_cos"].to(self.device)

        pred_deltas_norm, pred_frames_raw = [], []
        for step in range(self.cfg.rollout_steps):
            delta_norm_pred = self.model(window)  # (B,4,H,W)
            pred_deltas_norm.append(delta_norm_pred)

            delta_raw_pred = delta_norm_pred * self.delta_std + self.delta_mean
            next_dynamic_raw_pred = current_dynamic_raw + delta_raw_pred
            pred_frames_raw.append(next_dynamic_raw_pred)

            use_teacher = random.random() < tf_p
            next_dynamic_raw = (
                future_dynamic_raw[:, step] if use_teacher else next_dynamic_raw_pred
            )

            next_full_norm = self._attach_and_normalize(
                next_dynamic_raw, future_hour_sin[:, step], future_hour_cos[:, step]
            )
            window = torch.cat([window[:, 1:], next_full_norm.unsqueeze(1)], dim=1)
            current_dynamic_raw = next_dynamic_raw

        pred_deltas_norm = torch.stack(
            pred_deltas_norm, dim=1
        )  # (B,rollout_steps,4,H,W)
        pred_frames_raw = torch.stack(pred_frames_raw, dim=1)

        loss = (
            sum(
                self.loss_fn(pred_deltas_norm[:, s], future_deltas_norm[:, s])
                for s in range(self.cfg.rollout_steps)
            )
            / self.cfg.rollout_steps
        )

        return {
            "loss": loss,
            "pred_frames_raw": pred_frames_raw,
            "target_frames_raw": future_dynamic_raw,
            "anchor_raw": batch["anchor_dynamic_raw"].to(self.device),
        }

    def train_epoch(self, epoch: int) -> float:
        """Sets the model to training mode and iterates over the entire training DataLoader"""
        self.model.train()
        tf_p = tf_p_for_epoch(epoch, self.cfg)
        total_loss, n_batches = 0.0, 0
        for batch in self.train_loader:
            self.optimizer.zero_grad()
            out = self._rollout(batch, tf_p)
            out["loss"].backward()
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), self.cfg.grad_clip_norm
            )
            self.optimizer.step()
            total_loss += out["loss"].item()
            n_batches += 1
        self.scheduler.step()
        return total_loss / max(n_batches, 1)

    def validate_epoch(self) -> tuple[float, dict]:
        """
        Sets the model to evaluation mode (disabling gradients) and processes
        the validation DataLoader
        """
        self.model.eval()
        total_loss, n_batches = 0.0, 0
        tracker = MetricTracker(num_steps=self.cfg.rollout_steps)
        with torch.no_grad():
            for batch in self.val_loader:
                out = self._rollout(batch, tf_p=0.0)
                total_loss += out["loss"].item()
                n_batches += 1

                pred = out["pred_frames_raw"].cpu().numpy()
                target = out["target_frames_raw"].cpu().numpy()
                anchor = out["anchor_raw"].cpu().numpy()
                persistence = np.repeat(anchor[:, None], self.cfg.rollout_steps, axis=1)
                tracker.update(pred, target, persistence)
        return total_loss / max(n_batches, 1), tracker.compute()

    def fit(self, num_epochs: int, early_stopping_patience: int = 10) -> None:
        """
        calls train_epoch and validate_epoch sequentially,
        prints the progress to the console, tracks the best validation loss,
        and stops training early if the model fails to improve after a set number of epochs
        """
        epochs_without_improvement = 0
        for epoch in range(num_epochs):
            train_loss = self.train_epoch(epoch)
            val_loss, val_metrics = self.validate_epoch()
            tf_p = tf_p_for_epoch(epoch, self.cfg)
            print(
                f"epoch {epoch:03d}  tf_p={tf_p:.2f}  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}"
            )

            is_best = val_loss < self.best_val_loss
            if is_best:
                self.best_val_loss = val_loss
                epochs_without_improvement = 0
                self.save_checkpoint(epoch, val_metrics, is_best=True)
            else:
                epochs_without_improvement += 1
                if epochs_without_improvement >= early_stopping_patience:
                    print(
                        f"Early stopping at epoch {epoch} (no improvement for {early_stopping_patience} epochs)"
                    )
                    break

    def save_checkpoint(
        self, epoch: int, val_metrics: dict, is_best: bool = False
    ) -> None:
        """
        Whenever the validation loss reaches a new low, this method serializes
        the model weights to a
        model.pt file and dumps the performance metrics to a metadata.json
        file inside the app/artifact_store/weather_convlstm/LATEST directory.
        """
        if not is_best:
            return
        out_dir = Path("app/artifact_store/weather_convlstm/LATEST")
        out_dir.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), out_dir / "model.pt")
        import json

        (out_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "epoch": epoch,
                    "val_loss": self.best_val_loss,
                    "val_metrics": val_metrics,
                },
                indent=2,
            )
        )
        print(f"  saved checkpoint -> {out_dir}")


def build_normalizers(
    npz_paths: list[str], static_tensor: np.ndarray
) -> tuple[RawChannelNormalizer, DeltaNormalizer]:
    """
    loops through raw .npz to extract a subset of the historical frames and target deltas
    it attaches the static terrain and cyclic time embeddings to these frames, then fits the 2 normalizers
    so they can sclae data correctly before it hits the NN
    """
    raw_frames, delta_frames = [], []
    for p in npz_paths:
        data = np.load(p)
        hourly = data["hourly_tensor"][::24]
        timestamps = [str(t) for t in data["hourly_timestamps"][::24]]
        hs, hc = _hour_angle(timestamps)
        full = attach_static_and_time(hourly, static_tensor, hs, hc)  # (T,9,H,W)
        raw_frames.append(full)
        delta_frames.append(data["hourly_deltas"])

    raw_all = np.concatenate(raw_frames, axis=0)
    delta_all = np.concatenate(delta_frames, axis=0)

    raw_norm = RawChannelNormalizer()
    raw_norm.fit(raw_all)
    delta_norm = DeltaNormalizer()
    delta_norm.fit(delta_all)
    return raw_norm, delta_norm


def main() -> None:
    """
    the CLI entrypoint for the script
    parses CL arguments, sets random seeds, loads datasets, configs DataLoader instances
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--weather-tensors-dir", default=TrainConfig.weather_tensors_dir)
    ap.add_argument("--static-tensor-path", default=TrainConfig.static_tensor_path)
    ap.add_argument("--epochs", type=int, default=TrainConfig.epochs)
    ap.add_argument("--batch-size", type=int, default=TrainConfig.batch_size)
    args = ap.parse_args()

    cfg = TrainConfig(
        weather_tensors_dir=args.weather_tensors_dir,
        static_tensor_path=args.static_tensor_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
    )
    torch.manual_seed(cfg.seed)
    random.seed(cfg.seed)

    npz_paths = sorted(
        str(p) for p in Path(cfg.weather_tensors_dir).glob("weather_tensors_*.npz")
    )
    if not npz_paths:
        raise FileNotFoundError(
            f"No weather_tensors_*.npz found in {cfg.weather_tensors_dir} — "
            "run app.backend.ml.training.build_weather_dataset first."
        )

    static_path = Path(cfg.static_tensor_path)
    if not static_path.exists():
        raise FileNotFoundError(
            f"{static_path} not found — static rasters (elevation/slope/aspect) "
            "haven't been wired up yet."
        )
    static_tensor = np.load(static_path)["static_tensor"]

    raw_norm, delta_norm = build_normalizers(npz_paths, static_tensor)

    split_cfg = WeatherDatasetSplitConfig(
        input_hours=cfg.input_hours, rollout_steps=cfg.rollout_steps
    )
    full_dataset = WeatherRolloutDataset(
        npz_paths, static_tensor, raw_norm, delta_norm, split_cfg
    )

    n_val = int(len(full_dataset) * cfg.val_fraction)
    n_train = len(full_dataset) - n_val
    train_set, val_set = random_split(
        full_dataset,
        [n_train, n_val],
        generator=torch.Generator().manual_seed(cfg.seed),
    )
    # NOTE: random_split here is a placeholder — the real framing calls for
    # a TIME-BASED split (contiguous months/fire-seasons), not a random one,
    # to avoid leaking near-identical adjacent hours into validation. Swap
    # this out once the fire-season stratification approach is settled.

    train_loader = DataLoader(train_set, batch_size=cfg.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=cfg.batch_size, shuffle=False)

    model_cfg = WeatherDeltaModelConfig(
        hidden_dims=cfg.hidden_dims, kernel_size=cfg.kernel_size
    )
    model = WeatherDeltaModel(model_cfg)

    trainer = Trainer(
        model, train_loader, val_loader, static_tensor, raw_norm, delta_norm, cfg
    )
    trainer.fit(cfg.epochs)


if __name__ == "__main__":
    main()