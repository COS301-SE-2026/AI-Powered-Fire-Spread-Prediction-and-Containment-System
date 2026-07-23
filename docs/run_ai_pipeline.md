# In the terminal, run the following commands to run the DCA simulation

- Note: This is dependent on the XGBoost ignition model already being trained and published. Run the commands in the run_XGBoost.md before the commands in this document.

1. Ensure you are in the project root and the same environment variables from the ignition training are still in terminal session.
```base
export FIRE_ARTIFACT_STORE=/tmp/fire-test-score
export PYTHONPATH=app/backend/src:app/ml
```

2. Run the dca pipeline. Uses the ignition scores from xgboost model and the runs the CA from PyTorchFire
```bash
python -m app.backend.src.ai.run_ai_pipeline
```

3. Output should be similar to the following:

DCA is running | device currently being used: device=cuda

tick |  burning |  burned
------
   0 |        1 |       0
   1 |        6 |       0
   2 |       18 |       3
   3 |       31 |      11
   4 |       56 |      19
   5 |       73 |      38
   6 |       90 |      66
   7 |      110 |     103
   8 |      125 |     148
   9 |      146 |     196
  10 |      151 |     252
  11 |      147 |     318
  12 |      148 |     382
  13 |      167 |     437
  14 |      160 |     520
  15 |      147 |     592