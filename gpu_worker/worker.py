# Polls fire-system-gpu-inference for jobs, runs the fire-spread model and publishes the results to fire-system-gpu-results
import json
import logging
import os
import time
from pathlib import Path

import boto3
import numpy as np
import requests
import torch

from ml.models.nowcast_model import WeatherDeltaModel
from app.backend.src.ai.dca import run_dca
from app.backend.src.ai.model_pipeline import run_convlstm_dca

AWS_REGION = os.environ.get("AWS_REGION")
INFERENCE_QUEUE_URL = os.environ.get("INFERENCE_QUEUE_URL")
RESULTS_QUEUE_URL = os.environ.get("RESULTS_QUEUE_URL")

WORKER_ID = os.environ.get("WORKER_ID", "gpu-worker-1")

# Mounted S3 bucket (via mount-s3 / fire-system-artifacts.service).
# Models are read from here. Large results are written here too since SQS
# messages are capped at 256KB and simulation output can easily exceed that
ARTIFACTS_ROOT = Path(os.environ.get("ARTIFACTS_ROOT", "/mnt/firefighter-system-artifacts"))
RESULTS_DIR = ARTIFACTS_ROOT / "results"

CONVLSTM_CHECKPOINT_PATH = ARTIFACTS_ROOT / "models" / "weather_convlstm" / "LATEST" / "model.pt"
DCA_PARAMS_PATH = ARTIFACTS_ROOT / "models" / "dca_params" / "calibrated_params.json"

# fallback DCA params if calibrated_params.json isn't present on the mount
DEFAULT_DCA_PARAMS = {
    "a": 0.015,
    "p_h": 0.06,
    "c_1": 0.04,
    "c_2": 0.03,
    "p_continue": 0.6,
}

# fixed model input shape, per contract with model_pipeline.py 
GRID_H = 64
GRID_W = 64
WEATHER_HISTORY_LENGTH = 6  # T=6 past hourly frames

# DCA tick conversion: 15 min/tick -> 4 ticks/hour
TICKS_PER_HOUR = 4
MAX_STEPS = 288     # 72 hours max simulation time

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

sqs = boto3.client("sqs", region_name=AWS_REGION)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_convlstm_model() -> WeatherDeltaModel:
    """
    Loads the trained ConvLSTM checkpoint fron the mounted artifacts bucket per teammate's
    exact loading contract:
    
        checkpoint = torch.load("app/artifact_store/weather_convlstm/LATEST")
        model.load_state_dict(checkpoint["model_state_dict"])
    """
    model = WeatherDeltaModel()
    checkpoint = torch.load(CONVLSTM_CHECKPOINT_PATH, map_location=DEVICE)
    # If wrapped in a dict with 'model_state_dict', unwrap it; otherwise use directly
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]
    else:
        state_dict = checkpoint
    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()
    
    log.info("Loaded ConvLSTM checkpoin from %s", CONVLSTM_CHECKPOINT_PATH)
    return model

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
    
# Loaded once at process startup, not per-job - model weights stay resident in memory/GPY across
# every job worker picks up. Wrapped so import doesn't hard-crash when checkpoint isn't available yet.
# Individual jobs will fail with a clear error instead if inference is actually attempted without a model
try:
    convlstm_model = load_convlstm_model()
except FileNotFoundError as e:
    log.warning("ConvLSTM checkppoint not available yet (%s) - inference will fail until it exists", e)
    convlstm_model = None
default_dca_params = load_dca_params()

def build_ignition_mask(center_lat: float, center_lon: float, grid_bounds: list) -> np.ndarray:
    """
    Builds a (64, 64) boolean ignition mask with a single True cell at the grid position closest to
    (center_lat, center_lon).  grid_bounds is [min_lon, min_lat, max_lon, max_lat]
    """
    min_lon, min_lat, max_lon, max_lat = grid_bounds
  
    row = int(np.clip((max_lat - center_lat) / (max_lat - min_lat) * GRID_H, 0, GRID_H - 1))
    col = int(np.clip((center_lon - min_lon) / (max_lon - min_lon) * GRID_W, 0, GRID_W -1))
    
    mask = np.zeros((GRID_H, GRID_W), dtype=bool)
    mask[row, col] = True
    return mask

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
                frame["rel_humidity"],
                frame["temperature"],
            ],
            axis=0,
        ).astype(np.float32)
        frames.append(stacked)
        
    sequence = np.stack(frames, axis=0) # [T, 4, H, W]
    tensor = torch.from_numpy(sequence).unsqueeze(0)    #[1, T, 4, H, W]
    return tensor

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather_history(job: dict) -> list:
    """
    Fetches the WEATHER_HISTORY_LENGTH hours of weather from Open-Meteo for the fire's
    center point, and broadcasts each hourly point value uniformly across the (GRID_H, GRID_W) grid.
    """
    params = {
        "latitude": job["center_lat"],
        "longitude": job["center_lon"],
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
        "wind_speed_unit": "ms",
        "past_hours": WEATHER_HISTORY_LENGTH,
        "forecast_hours": 1,
        "timezone": "UTC",
    }
    response = requests.get(OPEN_METEO_FORECAST_URL, params=params, timeout=10)
    response.raise_for_status()
    hourly = response.json()["hourly"]
    
    frames = []
    for i in range(WEATHER_HISTORY_LENGTH):
        temperature_c = hourly["temperature_2m"][i]
        rel_humidity_pct = hourly["relative_humidity_2m"][i]
        wind_speed_ms = hourly["wind_speed_10m"][i]
        wind_direction_deg = hourly["wind_direction_10m"][i]
        
        # convert speed + "from" direction (degrees) into u/v components
        direction_rad = np.radians(wind_direction_deg)
        wind_u = -wind_speed_ms * np.sin(direction_rad)
        wind_v = -wind_speed_ms * np.cos(direction_rad)
        
        frames.append(
            {
                "wind_u": np.full((GRID_H, GRID_W), wind_u, dtype=np.float32),
                "wind_v": np.full((GRID_H, GRID_W), wind_v, dtype=np.float32),
                "temperature": np.full((GRID_H, GRID_W), temperature_c, dtype=np.float32),
                "rel_humidity": np.full(
                    (GRID_H, GRID_W), rel_humidity_pct / 100.0, dtype=np.float32
                ),
            }
        )
    return frames
        
def fetch_static_grids(job: dict) -> dict:
    """
    Fetches static terrain grids for the job's bounding box.
    """
    from ai.resolve_tiles import resolve_dem_path, resolve_sentinel2_bands
    from ml.features.terrain import extract_terrain_features
    from ml.features.fuel_load import process_sentinal2_and_worldcover
    
    min_lon, min_lat, max_lon, max_lat = job["grid_bounds"]
    target_shape = (GRID_H, GRID_W)
    
    dem_paths = resolve_dem_path(min_lon, min_lat, max_lon, max_lat)
    if len(dem_paths) > 1:
        log.warning("bbox spans %d DEM tiles, only using first (%s) - terrain will be wrong near the edge",
                    len(dem_paths),
                    dem_paths[0],
                    )
        
    terrain = extract_terrain_features(
        dem_paths[0], min_lon, min_lat, max_lon, max_lat, target_shape=target_shape
    )
    
    # aspect comes back in degrees (0-360); dca.py's static_grids convention
    # is aspect_sin/aspect_cos, matching how it's already stored elsewhere.
    aspect_rad = np.radians(terrain["aspect"])
    aspect_sin = np.sin(aspect_rad).astype(np.float32)
    aspect_cos = np.cos(aspect_rad).astype(np.float32)
    
    s2 = resolve_sentinel2_bands(min_lon, min_lat, max_lon, max_lat)
    
    vegetation = process_sentinal2_and_worldcover(
        b04_path=s2.b04_path,
        b08_path=s2.b08_path,
        b11_path=s2.b11_path,
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        target_shape=target_shape,
        scl_path=s2.scl_path,
    )
    
    return {
        "elevation": terrain["elevation"],
        "slope": terrain["slope"],
        "aspect_sin": aspect_sin,
        "aspect_cos": aspect_cos,
        "fuel_load": vegetation["fuel_load"],
        "dryness": vegetation["dryness"],
    }
        

def run_inference(job: dict) -> dict:
    # 'job' is whatever payload app side published to fire-system-gpu-inference.
    # Must return a JSON-serializable dict. Needs enough identifying info (min 'job_id' and 'region_id')so backend's results-consumer background task can key result correctly in Valkey
   
    if convlstm_model is None:
        raise RuntimeError("ConvLSTM model not loaded - checkpoint missing at "
                           f"{CONVLSTM_CHECKPOINT_PATH}. Cannot run inference")
    
    job_id = job.get("job_id", job.get("fire_id"))
    region_id = job.get("region_id", job.get("fire_id"))
    
    weather_history = fetch_weather_history(job)
    weather_history_tensor = build_weather_history_tensor(weather_history)
    
    static_grids = fetch_static_grids(job)
    
    ignition_mask = build_ignition_mask(
        center_lat=job["center_lat"],
        center_lon=job["center_lon"],
        grid_bounds=job["grid_bounds"],
    )
    
    n_steps = min(job.get("duration_hours", 4) * TICKS_PER_HOUR, MAX_STEPS)
    
    raw_params = job.get("params", default_dca_params)
    params = {
        k: torch.as_tensor(v, dtype=torch.float32)
        for k, v in raw_params.items()
    }
    
    history = run_convlstm_dca(
        convlstm_model=convlstm_model,
        weather_history=weather_history_tensor,
        static_grids=static_grids,
        cell_size_m=job.get("cell_size_m", 15.0),
        n_steps=n_steps,
        ignition_mask=ignition_mask,
        containment_lines=job.get("containment_lines"),
        grid_bounds=job["grid_bounds"],
        params=params,
    )
    

    return {
        "job_id": job_id,
        "region_id": region_id,
        "history": [grid.tolist() for grid in history],
    }
    
def write_result_to_artifacts(job_id: str, result: dict) -> str:
    """
    Writes the full results to mounted artifacts bucket and returns the path. Keeps SQS messages
    small by only ever putting a pointer on the results queue, not the payload itself
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / f"{job_id}.json"
    result_path.write_text(json.dumps(result))
    return str(result_path)

def touch_heartbeat() -> None:
    HEARTBEAT_FILE.write_text(str(time.time()))

def handle_message(message: dict) -> None:
    body = json.loads(message["Body"])
    job_id = body.get("job_id", "<unknown>")
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
