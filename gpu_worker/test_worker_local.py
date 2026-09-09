"""
Local smome test for worker.py's data pipeline, without needing SQS, systemd or the full EC2 deployment.

Run from gpu_worker/ 

    python test_worker_local.py
    
Requires same environment variables worker.py needs at import time
(AWS_REGION, INFERENCE_QUEUE_URL, RESULTS_QUEUE_URL) even though this script never 
actually touches SQS.
"""

import json
import sys
import numpy as np
import worker

# A fake job matching the sample payload structure. Coordinates are a real location
FAKE_JOB = {
    "fire_id": "test_fire_001",
    "center_lat": -33.957,
    "center_lon": 18.461,
    "start_time": "2024-01-22T10:00:00Z",
    "duration_hours": 4,
    "cell_size_m": 15.0,
    "grid_bounds": [18.381, -34.037, 18.541, -33.877],
    "params": {
        "a": 0.015,
        "p_h": 0.06,
        "c_1": 0.04,
        "c_2": 0.03,
        "p_continue": 0.6,
    },
}

def run_step(name, fn):
    print(f"\n{'=' * 60}\n{name}\n{'=' * 60}")
    try:
        result = fn()
        print(f"OK - {name} succeeded")
        return result
    except Exception as e: # pylint: disable=broad-exception-caught
        import traceback
        traceback.print_exc()
        print(f"FAILED - {name}: {type(e).__name__}: {e}")
        return None
    
def main():
    print("Testing worker.py pipeline stages independently...")
    print(f"ConvLSTM model loaded: {worker.convlstm_model is not None}")
    
    ignition_mask = run_step(
        "build_ignition_mask",
        lambda: worker.build_ignition_mask(
            FAKE_JOB["center_lat"], FAKE_JOB["center_lon"], FAKE_JOB["grid_bounds"]
        ),
    )
    if ignition_mask is not None:
        print(f" shape={ignition_mask.shape}, true_count={ignition_mask.sum()}")
        
    weather_history = run_step(
        "fetch_weather_history (real Open-Meteo API call)",
        lambda: worker.fetch_weather_history(FAKE_JOB),
    )
    if weather_history is not None:
        print(f" frames={len(weather_history)}, keys={list(weather_history[0].keys())}")
        print(f" wind_u sample value={weather_history[0]['wind_u'][0, 0]:.2f}")
        
    static_grids = run_step(
        "fetch_static_grids (real DEM + Sentinel-2 fetch, may be slow)",
        lambda: worker.fetch_static_grids(FAKE_JOB),
    )
    if static_grids is not None:
        for key, grid in static_grids.items():
            print(f" {key}: shape={grid.shape}, min={grid.min():.3f}, max={grid.max():.3f}")
    
    if weather_history is not None:
        tensor = run_step(
            "build_weather_history_tensor",
            lambda: worker.build_weather_history_tensor(weather_history),
        )
        if tensor is not None:
            print(f" shape={tuple(tensor.shape)}")
            
    if worker.convlstm_model is not None and weather_history is not None and static_grids is not None:
        result = run_step(
            "run_inference (FULL pipeline - LSTM + DCA)",
            lambda: worker.run_inference(FAKE_JOB),
        )
        if result is not None:
            print(f" job_id={result['job_id']}, history_steps={len(result['history'])}")
    else:
        print(f"\nSkipping full run_inference - model not loaded or prior steps failed.")
        print("(This is expected if the ConvLSTM checkpoint doesn't exist yet)")
    
    print("\nDone")
    
if __name__ == "__main__":
    main()