# In the terminal, run the following commands to train the XGBoost ignition model

- Note: The model is trained on a dataset built from real NASA FIRMS detections, Sentinel-2 imagery and Copernicus DEM terrain. Steps 2 and 3 download and process that data. If a trained model is already published, skip to run_DCA.md.

1. Ensure you are in the project root, activate the virtual environment and set the environment variables.
```bash
source .venv/bin/activate
export FIRE_ARTIFACT_STORE=/tmp/fire-test-store
export PYTHONPATH=app/backend/src:app/ml
```

2. Build the training manifest. Finds fire events in the FIRMS detections and downloads the least-cloudy Sentinel-2 scene for each one.
```bash
python -m ai.build_training_manifest --csv raw_data/fire_nrt_J2V-C2_778685.csv --out raw_data/static_manifest.csv --top-n 5
```

- Note: paths are given relative to `app/datasets/`, not the project root. Arguments resolving outside that directory are rejected.
- Runtime: several minutes per fire. Each downloads three Sentinel-2 bands at 100-500 MB.

3. Output should be similar to the following:

```
Fire ID: 1886 | using scene S2B_34JGQ_20250714_0_L2A with cloud cover 2.4%
Fire ID: 2201 | using scene S2A_35JLL_20251009_0_L2A with cloud cover 11.7%
skip fire id: 4417: no sent 2 scene under the max cloud cover of 30%
Fire ID: 11470 | using scene S2A_35JMK_20250802_0_L2A with cloud cover 0.9%

 wrote 3/5 manifest rows to raw_data/static_manifest.csv
```

4. Build the ignition dataset. Crops the rasters per fire, fetches historical weather, and assembles the 14-feature training matrix.
```bash
python -m training.build_real_dataset --manifest app/datasets/raw_data/static_manifest.csv --out app/datasets/raw_data/ignition_dataset.npz
```

5. Output should be similar to the following:

```
150,558 total detections loaded from app/datasets/raw_data/fire_nrt_J2V-C2_778685.csv
25903 distinct fires
6,581 fires that have more than 2 ticks
Fetching historical weather for fire_11470 (-26.3745, 28.4826)
Saved 1,176 hourly weather records
Fetching historical weather for fire_1886 (-26.5504, 29.1648)
Saved 1,392 hourly weather records

wrote app/datasets/raw_data/ignition_dataset.npz
  X         (454536, 14) float32
  y         (454536,) float32
  fires     3 -> [1886, 11470, 23443]
  positives 199 / 454536  (0.00044)
```

6. Train the model and publish it to the artifact store.
```bash
python -m training.train_ignition --data app/datasets/raw_data/ignition_dataset.npz --device cuda --promote
```

- Use `--device cpu` if no NVIDIA GPU is available.
- Omit `--promote` to train without replacing the currently active model.

7. Output should be similar to the following:

```
Train rows: 304,982 | val rows: 149,554 |
Positives: 0.03% |
Scale_pos_weight: 3079.6 | device: cuda
[0]     train-aucpr:0.01807     val-aucpr:0.01072
[50]    train-aucpr:0.09872     val-aucpr:0.00992
Feature importance (gain):
dist_to_fire              10090.6
n_burning_neighbours       3158.5
upwind_burning             2207.9
slope                      2094.9
elevation                  1806.7
wind_v                     1776.7
fuel_load                  1679.0
dryness                    1628.7
temperature                1625.1
aspect_cos                 1580.5
aspect_sin                 1473.3
wind_u                     1462.1
rel_humidity               1068.3
downslope_burning           197.6
Published: ignition/v20260730-161739-c92bac_cachyos-x8664 (promoted to LATEST)
```

- PR-AUC is used rather than accuracy or ROC-AUC because the positive class is under 0.1% of rows. It must be read against the base rate: a random classifier scores approximately the positive rate.
- The train/validation split is by fire event, not by row. Consecutive timesteps of the same fire are near-duplicates, so a random split would leak them across both sides.

8. Confirm the model published correctly.
```bash
python -c "from ai.ignition import IgnitionScorer; s = IgnitionScorer.load('LATEST'); print(s.metadata['version'], s.metadata['data_source'], round(s.metadata['val_aucpr'], 4))"
```

9. Output should be similar to the following:

```
v20260730-161739-c92bac_cachyos-x8664 app/datasets/raw_data/ignition_dataset.npz 0.0166
```

- If `data_source` reads `synthetic`, the `--data` flag was omitted in step 6 and the model was trained on generated placeholder data rather than the real dataset.

10. The model is now published. Continue with run_DCA.md.