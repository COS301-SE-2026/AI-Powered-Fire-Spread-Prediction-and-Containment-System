# Polls fire-system-gpu-inference for jobs, runs the fire-spread model and publishes the results to fire-system-gpu-results
import json
import logging
import os
import time
from pathlib import Path

import base64
import zlib
import boto3
import numpy as np
import requests
import torch

from app.backend.src.ai.simulation import (
    build_boundary_ignition_mask,
    build_multi_boundary_ignition_mask,
)
#from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.model_pipeline import run_convlstm_dca, load_weather_forecaster, WeatherForecaster
from app.backend.src.ai.sim_constants import MAXSTEPS, TICKS_PER_HOUR
from app.backend.src.ai.job_builder import fetch_static_grids, fetch_weather_history, DEFAULT_DCA_PARAMS

AWS_REGION = os.environ.get("AWS_REGION")
INFERENCE_QUEUE_URL = os.environ.get("INFERENCE_QUEUE_URL")
RESULTS_QUEUE_URL = os.environ.get("RESULTS_QUEUE_URL")
WORKER_ID = os.environ.get("WORKER_ID", "gpu-worker-1")

ARTIFACTS_ROOT = Path(os.environ.get("ARTIFACTS_ROOT", "/mnt/fire-system-artifacts"))
ARTIFACTS_S3_BUCKET = os.environ.get("ARTIFACTS_S3_BUCKET", "fire-system-artifacts-827257544258")

sqs = boto3.client("sqs", region_name=AWS_REGION)
s3 = boto3.client("s3", region_name=AWS_REGION)
# Mounted S3 bucket (via mount-s3 / fire-system-artifacts.service).
# Models are read from here. Large results are written here too since SQS
# messages are capped at 256KB and simulation output can easily exceed that

RESULTS_DIR = ARTIFACTS_ROOT / "results"
CONVLSTM_MODEL_DIR = Path(os.environ.get(
    "CONVLSTM_MODEL_DIR",
    str(ARTIFACTS_ROOT / "models" / "weather_convlstm" / "LATEST")
))
DCA_PARAMS_PATH = ARTIFACTS_ROOT / "models" / "dca_params" / "calibrated_params.json"


WEATHER_HISTORY_LENGTH = 6  # T=6 past hourly frames
MAX_STEPS = MAXSTEPS 

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(
    "gpu_worker"
)  # Logs go to local systemd journal only (journalctl -u fire-worker)

# Where systemd unit's monitoring checks for liveness

HEARTBEAT_FILE = Path(os.environ.get("HEARTBEAT_FILE", "/tmp/gpu_worker_heartbeat")) # NOSONAR

# SQS long-polling wait time
WAIT_TIME_SECONDS = 20

# How long a message is invisible to other workers while this one processes it.
# Needs to be longer than model's worst-case inference time, so we gonna have to play around with this value
VISIBILITY_TIMEOUT_SECONDS = 300



DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_convlstm_model() -> WeatherForecaster | None:
    """
    Loads model and its normalizers
    """
    try:
        forecaster = load_weather_forecaster(CONVLSTM_MODEL_DIR, DEVICE)
        log.info("Loaded convLSTM forecaster from %s", CONVLSTM_MODEL_DIR)
        return forecaster
    except Exception as err:
        log.warning("Could not load ConvLSTM from %s (%s). Simulations will use current weather", CONVLSTM_MODEL_DIR, err)
        return None

# loaded once to keep weights on gpu across the job
convlstm_forecaster = load_convlstm_model()
default_dca_params = dict(DEFAULT_DCA_PARAMS)

def load_dca_params() -> dict:
    """
    Loads calibrated DCA params from the mounted artifacts bucket, falling back to the hardcoded
    defaults if the file isn't present
    """
    try:
        return json.loads(DCA_PARAMS_PATH.read_text())
    except FileNotFoundError:
        log.warning(
            "calibrated_params.json not found at %s, using hardcoded defaults",
            DCA_PARAMS_PATH,
        )
        return dict(DEFAULT_DCA_PARAMS)

# def build_ignition_mask(center_lat: float, center_lon: float, grid_bounds: list, grid_h: int, grid_w: int) -> np.ndarray:
#     min_lon, min_lat, max_lon, max_lat = grid_bounds
  
#     row = int(np.clip((max_lat - center_lat) / (max_lat - min_lat) * grid_h, 0, grid_h - 1))
#     col = int(np.clip((center_lon - min_lon) / (max_lon - min_lon) * grid_w, 0, grid_w -1))
    
#     mask = np.zeros((grid_h, grid_w), dtype=bool)
#     mask[row, col] = True
#     return mask

def build_weather_history_tensor(weather_history: list) -> torch.Tensor:
    """
    Converts a list of WEATHER_HISTORY_LENGTH hourly frames into the 
    [1, T, 4, H, W] tensor the ConvLSTM expects
    """
    frames = []
    for frame in weather_history:
        stacked = np.stack(
            [
                frame["wind_u"],
                frame["wind_v"],
                frame["temperature"],
                frame["rel_humidity"],
            ],
            axis=0,
        ).astype(np.float32)
        frames.append(stacked)
        
    sequence = np.stack(frames, axis=0) # [T, 4, H, W]
    tensor = torch.from_numpy(sequence).unsqueeze(0)    #[1, T, 4, H, W]
    return tensor

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast" 

def run_inference(job: dict) -> dict:
    # 'job' is whatever payload app side published to fire-system-gpu-inference.
    # Must return a JSON-serializable dict. Needs enough identifying info (min 'job_id' and 'region_id')so backend's results-consumer background task can key result correctly in Valkey
    
    job_id = job.get("job_id", job.get("fire_id"))
    region_id = job.get("region_id", job.get("fire_id"))
    
    weather_history = fetch_weather_history(job)
    weather_history_tensor = build_weather_history_tensor(weather_history)
    
    static_grids = fetch_static_grids(job)

    fires = job.get("fires")
    if fires:
        ignition_mask = build_multi_boundary_ignition_mask(
            H=job["grid_h"],
            W=job["grid_w"],
            cell_size_m=job["cell_size_m"],
            fires=[
                (f["center_lat"], f["center_lon"], f["boundary_radius_m"])
                for f in fires
            ],
            grid_bounds=tuple(job["grid_bounds"]),
        )
    else:
        ignition_mask = build_boundary_ignition_mask(
            H=job["grid_h"],
            W=job["grid_w"],
            cell_size_m=job["cell_size_m"],
            boundary_radius_m=job["boundary_radius_m"]
        )
    
    n_steps = int(job.get("n_steps", min(job.get("duration_hours", 4) * TICKS_PER_HOUR, MAX_STEPS)))
    
    raw_params = job.get("params", default_dca_params)
    params = {
        k: torch.as_tensor(v, dtype=torch.float32)
        for k, v in raw_params.items()
    }
    
    history = run_convlstm_dca(
        forecaster=convlstm_forecaster,
        weather_history=weather_history_tensor,
        static_grids=static_grids,
        cell_size_m=job["cell_size_m"],
        n_steps=n_steps,
        ignition_mask=ignition_mask,
        containment_lines=job.get("containment_lines"),
        grid_bounds=job["grid_bounds"],
        params=params,
    )
    

    hist = np.stack([
        (g.detach().cpu().numpy() if hasattr(g, "detach") else np.asarray(g)).astype(np.int8)
        for g in history
    ])
    
    return {
        "job_id": job_id,
        "region_id": region_id,
        "status": "completed",
        "history_z": base64.b64encode(zlib.compress(hist.tobytes(), 6)).decode("ascii"),
        "history_shape": list(hist.shape),
    }
    
def write_result_to_artifacts(job_id: str, result: dict) -> str:
    """
    Writes the full results to mounted artifacts bucket and returns the path. Keeps SQS messages
    small by only ever putting a pointer on the results queue, not the payload itself
    """
    s3_key = f"results/{job_id}.json"
    payload = json.dumps(result).encode("utf-8")

    s3.put_object(
        Bucket=ARTIFACTS_S3_BUCKET,
        Key=s3_key,
        Body=payload,
        ContentType="application/json"
    )
    log.info("Uploaded sim output to s3://%s/%s", ARTIFACTS_S3_BUCKET, s3_key)
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        local_path = RESULTS_DIR / f"{job_id}.json"
        local_path.write_bytes(payload)
    except Exception as err:
        log.warning("Could not mirror file to local mount: %s", err)

    return f"s3://{ARTIFACTS_S3_BUCKET}/{s3_key}"

def touch_heartbeat() -> None:
    HEARTBEAT_FILE.write_text(str(time.time()))

def handle_message(message: dict) -> None:
    body = json.loads(message["Body"])
    job_id = body.get("job_id", "<unknown>")

    expires_at = body.get("expires_at")
    if expires_at and time.time() > expires_at:
        log.info("Skipping expired job %s: the backend already stopped waiting for it", job_id)
        sqs.delete_message(QueueUrl=INFERENCE_QUEUE_URL, ReceiptHandle=message["ReceiptHandle"])
        return

    log.info("Processing job %s", job_id)

    result = run_inference(body)
    result_path = write_result_to_artifacts(job_id, result)

    sqs.send_message(
        QueueUrl=RESULTS_QUEUE_URL,
        MessageBody=json.dumps(
                {
                    "job_id": result["job_id"],
                    "region_id": result["region_id"],
                    "status": "completed",
                    "result_path": result_path,
                    "worker_id": WORKER_ID,
                }
            ),
    )
    log.info("Published result for job %s -> %s", job_id, result_path)

    sqs.delete_message(
        QueueUrl=INFERENCE_QUEUE_URL,
        ReceiptHandle=message["ReceiptHandle"],
    )

def main() -> None:
    log.info("Worker starting. Polling %s", INFERENCE_QUEUE_URL)
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=INFERENCE_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=WAIT_TIME_SECONDS,
                VisibilityTimeout=VISIBILITY_TIMEOUT_SECONDS,
            )
            touch_heartbeat()

            messages = response.get("Messages", [])
            if not messages:
                continue

            for message in messages:
                try:
                    handle_message(message)
                except Exception:
                    log.exception(
                        "Failed to process job. Will retry after visibility timeout"
                    )  # Don't delete message on failure

        except Exception:
            # Back off briefly and keep going rather than crashing (If something goes wrong for whatever reason eg. AWS throttle
            log.exception("Error in polling loop, backing off")
            time.sleep(5)

if __name__ == "__main__":
    main()
