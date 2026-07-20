# In the terminal, run the following commands to train the model:

- Note: (For now) Every time you want to train, you gotta start from step 1 everytime

1. Ensure you are in the project root directory. Using /tmp for now. We will change it to a permanent location later when we figure out shared storage and have proper datasets. (so for now everytime you docker down, the trained data will be wiped out)
```bash
export FIRE_ARTIFACT_STORE=/tmp/fire-test-store
export PYTHONPATH=app/backend/src:app/ml
```
2. CPU training (verifies full pipeline before involving GPU / use this if you got no proper GPU)
```bash
python -m training.train_ignition --device cpu --promote
```
3. GPU training (if you have a proper GPU and want to use it). If you get output saying something about not finding a GPU, then install the drivers then reboot(`sudo dnf install akmod-nvidia xorg-x11-drv-nvidia-cuda`), but in the meantime it will default to using CPU
```bash
python -m training.train_ignition --device cuda --promote
```

Output should be similar to the following:
```
Train rows: 802,818 | val rows: 187,471 |
Positives: 15.89% |
Scale_pos_weight: 5.3 | device: cpu
[0]     train-aucpr:0.84690     val-aucpr:0.85504
[50]    train-aucpr:0.86361     val-aucpr:0.86906
[100]   train-aucpr:0.86687     val-aucpr:0.87014
[150]   train-aucpr:0.86858     val-aucpr:0.87003
[156]   train-aucpr:0.86880     val-aucpr:0.86999
Feature importance (gain):
n_burning_neighbours       8021.3
dist_to_fire               5882.4
downslope_burning           396.7
upwind_burning              389.8
rel_humidity                161.7
dryness                      76.6
fuel_load                    68.4
slope                        67.8
temperature                  47.0
wind_v                       20.9
elevation                    19.7
aspect_cos                   19.2
wind_u                       19.2
aspect_sin                   18.2
Published: ignition/v20260717-141253_fedora (promoted to LATEST)
```
4. Verify backend can consume what was just published
```bash
python -c "
from ai.ignition import IgnitionScorer
s = IgnitionScorer.load('LATEST')
print('version:', s.metadata['version'])
print('trained on device:', s.metadata['device'])
print('val PR-AUC:', round(s.metadata['val_aucpr'], 4))
"
```
The output should be similar to the following:
```
version: v20260717-141253_fedora
trained on device: cpu
val PR-AUC: 0.8702
```

# Run the backend tests for the model
- From root directory

1. Unit tests
```bash
yarn test:xgboost:unit
```