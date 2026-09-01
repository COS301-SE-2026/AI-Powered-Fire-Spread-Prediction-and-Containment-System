## Summary
Adds the full data pipeline and training setup for a ConvLSTM-based weather forecaster. Trains on real hourly weather deltas (not raw values), predicts residual change from the current state, and consumes existing terrain infrastructure from the ignition model rather than duplicating it.

## Data fetching
- Extended `app/datasets/scripts/fetch_historical_weather.py` with grid-fetch functions (`fetch_historical_weather_grid_sa`, `fetch_historical_weather_grid_year`, `build_sa_grid_coords`)
- Original per-fire `fetch_historical_weather()` function is untouched, so the ignition model's existing usage isn't affected

## Feature/target building (`app/ml/features/`)
- `weather_grid_loader.py`: pivots the long-format grid CSVs into `(T, 4, H, W)` tensors (channels: wind_u, wind_v, relative_humidity, temperature)
- `delta_targets.py`: computes deltas between consecutive hourly frames (the real training target)
- `temporal_targets.py`: hourly to 15-min linear interpolation, kept as a **post-hoc rendering step only** (see design note below), not used in training
- `normalization.py`: `RawChannelNormalizer` / `DeltaNormalizer`, two separate per-channel stat sets (raw values have much larger variance than deltas, sharing one normalizer would drown out the delta signal)
- `dem_source.py`: generalizes `build_training_manifest.py`'s `dem_vsis3_path()` (which resolves one DEM tile at a bbox's center, fine for a small per-fire patch) into a full Copernicus DEM GLO-30 tile-mosaic builder for the whole SA bbox (221 tiles), producing a VRT that `terrain.py`'s existing `extract_terrain_features()` can read directly

## Dataset & training (`app/ml/training/`)
- `build_weather_dataset.py` CLI: raw grid CSVs >> per-year `weather_tensors_<year>.npz` (hourly tensor, hourly deltas, cached 15-min interpolation for rendering)
- `build_static_dataset.py` CLI: builds the static terrain tensor (elevation, slope, aspect_sin, aspect_cos; aspect converted to sin/cos to match the ignition model's existing circular-encoding convention) via the reused `terrain.py`, auto-building the Copernicus DEM VRT if missing
- `dataset.py`: `WeatherRolloutDataset` (torch `Dataset`), slices `(input_hours history >> rollout_steps hourly rollout)` windows, attaches static + time-of-day channels; includes `split_by_month()` for a real time-based train/val split (avoids leaking near-identical adjacent hours into validation, which a random split would do)
- `losses.py`: `SmoothL1DeltaLoss`
- `metrics.py`: `MetricTracker`, RMSE + skill **vs. persistence baseline** per variable per rollout step
- `train_convlstm.py`: the actual training loop — multi-step rollout with **scheduled sampling** (teacher-forcing probability `tf_p` annealed from 1.0 to 0.25 across epochs), fully autoregressive validation (`tf_p=0`), checkpointing to `app/artifact_store/weather_convlstm/LATEST`

## Model (`app/ml/models/`)
- `conv_lstm_cell.py`, `conv_lstm.py`: standard multi-layer ConvLSTM
- `nowcast_model.py` - `WeatherDeltaModel`: ConvLSTM encoder + **zero-initialized** 1×1 conv head, so the untrained model starts exactly at the persistence baseline and is only trained to improve on it. Input channels: 10 (4 dynamic + 4 static + 2 time-of-day encoding), computed dynamically from the static tensor rather than hardcoded

## Key design decision
Model predicts **real hourly deltas** (genuine signal; depends on the full input history, not just two endpoints), not 15-min deltas. An earlier version trained directly on 15-min-interpolated deltas, but that made the training target and its own "naive baseline" the same array — no daylight for the model to add value. 15-min interpolation is now applied only after inference, for rendering/DCA-feed smoothness, never as a training signal.

## Verified locally

epoch 000 tf_p=1.00 train_loss=0.2223 val_loss=0.2074
epoch 001 tf_p=0.98 train_loss=0.1838 val_loss=0.1957
saved checkpoint -> app/artifact_store/weather_convlstm/LATEST

Loss decreasing across epochs, tf_p schedule tracking as expected — pipeline runs end-to-end.

## How to test
```bash
python -m app.datasets.scripts.fetch_historical_weather
python -m app.ml.training.build_weather_dataset
python -m app.ml.training.build_static_dataset
python -m app.ml.training.train_convlstm --epochs 50 --val-months 6 7 8 9 --batch-size 4
```