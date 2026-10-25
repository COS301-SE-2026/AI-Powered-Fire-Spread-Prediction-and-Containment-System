# for volunteer gpus
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from typing import Optional, Tuple
import base64
import zlib
import warnings

# pystac's storage extension warnings removal from terminal
warnings.filterwarnings("ignore", message="Could not parse bucket/account from href", category=UserWarning, module="pystac")

import numpy as np
import requests
import torch
import websockets

from app.backend.src.ai.model_pipeline import run_convlstm_dca, WeatherForecaster, load_weather_forecaster, model_summary, summarize_hourly_weather
from app.backend.src.ai.simulation import build_boundary_ignition_mask, build_multi_boundary_ignition_mask
from app.backend.src.ai.job_builder import fetch_static_grids, fetch_weather_history, DEFAULT_DCA_PARAMS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("volunteer_gpu_worker")

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")
REGISTRATION_KEY = os.getenv("REGISTRATION_KEY")
WORKER_LABEL = os.getenv("WORKER_LABEL", os.getenv("HOSTNAME", "volunteer-desktop"))
MODEL_DIR = os.getenv("MODEL_DIR", "app/artifact_store/models/weather_convlstm/LATEST")
CREDENTIALS_PATH = os.getenv("WORKER_CREDENTIALS_PATH", "/data/worker_credentials.json")

MIN_VRAM_MB = 3584
BENCHMARK_DURATION_SECONDS = 1.0
RECONNECT_DELAY_SECONDS = 5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def make_progress_reporter(websocket, loop: asyncio.AbstractEventLoop, job_id: str):
    """logs a stage of the model running and forwards it to the broker. Safe to call from the to_thread_worker thread"""
    def report(stage: str, message: str) -> None:
        log.info("%s (%s)", message, job_id)
        msg = json.dumps({"type": "progress", "job_id": job_id, "stage": stage, "message": message})
        try:
            asyncio.run_coroutine_threadsafe(websocket.send(msg), loop)
        except RuntimeError:
            pass
    return report

def load_saved_credentials() -> Optional[Tuple[str,str]]:
    try:
        with open(CREDENTIALS_PATH) as f:
            data = json.load(f)
        if data.get("access_token") and data.get("worker_id"):
            log.info("Using saved credentials for node %s", data["worker_id"])
            return data["access_token"], data["worker_id"]
    except FileNotFoundError:
        pass
    except (OSError, json.JSONDecodeError) as err:
        log.warning("Saved credentials unreadable (%s); ignoring them.", err)
    return None

def save_credentials(token: str, worker_id: str) -> None:
    os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
    tmp_path = f"{CREDENTIALS_PATH}.tmp"
    with open(tmp_path, "w") as f:
        json.dump({"access_token": token, "worker_id": worker_id}, f)
    os.chmod(tmp_path, 0o600)
    os.replace(tmp_path, CREDENTIALS_PATH)

def clear_saved_credentials() -> None:
    try:
        os.remove(CREDENTIALS_PATH)
    except FileNotFoundError:
        pass

def run_pre_flight_check() -> Tuple[bool, str, int]:
    log.info("Starting hardware qualification check...")

    if not torch.cuda.is_available():
        log.error("Hardware check failed: NVIDIA CUDA is not available.")
        return False, "", 0

    if torch.cuda.device_count() == 0:
        log.error("Hardware check failed: NO CUDA devices detected.")
        return False, "", 0

    device_props = torch.cuda.get_device_properties(0)
    gpu_name = device_props.name
    total_vram_mb = int(device_props.total_memory / (1024 * 1024))

    log.info("Detected GPU: %s (%d MB VRAM)", gpu_name, total_vram_mb)

    if total_vram_mb < MIN_VRAM_MB:
        log.error(
            "Hardware check failed: %d MB VRAM is below required %d MB baseline.",
            total_vram_mb,
            MIN_VRAM_MB,
        )
        return False, gpu_name, total_vram_mb

    log.info("Executing synthetic matrix stress test on CUDA...")
    try:
        x = torch.randn((4096, 4096), device="cuda:0", dtype=torch.float32)
        start_time = time.monotonic()
        iterations = 0

        while (time.monotonic() - start_time) < BENCHMARK_DURATION_SECONDS:
            _ = torch.matmul(x, x)
            torch.cuda.synchronize()
            iterations += 1

        del x
        torch.cuda.empty_cache()
        log.info("Benchmark complete: %d iterations executed successfully.", iterations)
    except Exception as err:
        log.error("Synthetic benchmark failed under load: %s", err)
        return False, gpu_name, total_vram_mb

    return True, gpu_name, total_vram_mb


def load_inference_model() -> Optional[WeatherForecaster]:
    """loads the weather model with its normalizers and metadata"""
    try:
        forecaster = load_weather_forecaster(MODEL_DIR, DEVICE)
        log.info("Loaded weather model from %s", MODEL_DIR)
        return forecaster
    except Exception as err:
        log.warning("Could not load the weather model from %s (%s). Simulations will use current weather without a forecast", MODEL_DIR, err)
        return None


def register_worker(reg_key: str, gpu_name: str, vram_mb: int) -> Optional[Tuple[str, str]]:
    endpoint = f"{BACKEND_BASE_URL}/api/v1/workers/register"
    payload = {
        "registration_key": reg_key,
        "label": WORKER_LABEL,
        "gpu_name": gpu_name,
        "vram_mb": vram_mb,
        "driver_version": torch.version.cuda or "unknown",
        "cuda_capable": True,
    }

    log.info("Claiming registration key with backend...")
    try:
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        token = data.get("access_token")
        worker_id = data.get("worker_id")
        if not token or not worker_id:
            log.error("Registration failed: Invalid response payload.")
            return None

        log.info("Worker verified and registered. Node ID: %s", worker_id)
        return token, worker_id
    except requests.exceptions.RequestException as err:
        log.error("Registration request failed: %s", err)
        return None


def execute_pipeline_task(forecaster: Optional[WeatherForecaster], payload: dict, report=lambda stage, message: None) -> dict:
    job_id = payload.get("job_id", "sim_task")
    log.info("Fetching remote terrain and weather data for job: %s", job_id)

    # fetch satelite and weather data
    report("fetching_weather", "Fetching weather data")
    weather_history = fetch_weather_history(payload)
    report("fetching_terrain", "Fetching terrain and satellite data")
    static_grids = fetch_static_grids(payload)

    # build the [1 T 4 H W] tensor for lstm
    frames = []
    for frame in weather_history:
        stacked = np.stack(
            [
                frame["wind_u"],
                frame["wind_v"],
                frame["temperature"],
                frame["rel_humidity"],
            ],
            axis=0
        ).astype(np.float32)
        frames.append(stacked)
    weather_tensor = torch.from_numpy(np.stack(frames, axis=0)).unsqueeze(0)

    fires = payload.get("fires")
    if fires:
        ignition_mask = build_multi_boundary_ignition_mask(
            H=payload["grid_h"],
            W=payload["grid_w"],
            cell_size_m=payload["cell_size_m"],
            fires=[(f["center_lat"], f["center_lon"], f["boundary_radius_m"]) for f in fires],
            grid_bounds=tuple(payload["grid_bounds"])
        )
    else:
        ignition_mask = build_boundary_ignition_mask(
            H=payload["grid_h"],
            W=payload["grid_w"],
            cell_size_m=payload["cell_size_m"],
            boundary_radius_m=payload["boundary_radius_m"]
        )

    

    raw_params = payload.get("params", DEFAULT_DCA_PARAMS)
    params = (
        {k: torch.as_tensor(v, dtype=torch.float32) for k, v in raw_params.items()}
        if raw_params
        else None
    )

    report("running_model", "Running fire spread model")
    history, hourly_weather = run_convlstm_dca(
        forecaster=forecaster,
        weather_history=weather_tensor,
        static_grids=static_grids,
        cell_size_m=payload["cell_size_m"],
        n_steps=payload["n_steps"],
        ignition_mask=ignition_mask,
        containment_lines=payload.get("containment_lines"),
        grid_bounds=payload.get("grid_bounds"),
        params=params,
    )

    report("packaging", "Packaging results")
    hist = np.stack([
        (g.detach().cpu().numpy() if hasattr(g, "detach") else np.asarray(g)).astype(np.int8)
        for g in history
    ])

    return {
        "job_id": job_id,
        "status": "completed",
        "history_z": base64.b64encode(zlib.compress(hist.tobytes(), 6)).decode("ascii"),
        "history_shape": list(hist.shape),
        "weather_by_hour": summarize_hourly_weather(hourly_weather),
        "forecast_source": "convlstm" if forecaster is not None else "current_weather",
        "forecast_model": model_summary(forecaster),
    }

async def run_worker_loop(forecaster: Optional[WeatherForecaster], worker_jwt: str):
    headers = {"Authorization" : f"Bearer {worker_jwt}"}

    while True:
        log.info("Connection to broker: %s", WEBSOCKET_URL)
        try:
            async with websockets.connect(
                WEBSOCKET_URL,
                additional_headers=headers,
                ping_interval=15,
                ping_timeout=5,
                max_size=None
            ) as websocket:
                log.info("Persistent WebSocket connection established. Node ready.")

                while True:
                    raw_msg = await websocket.recv()
                    data = json.loads(raw_msg)
                    msg_type = data.get("type")

                    if msg_type == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                        continue

                    if msg_type == "simulation_job":
                        job_payload = data.get("payload", {})
                        job_id = job_payload.get("job_id", "unknown")
                        report = make_progress_reporter(websocket, asyncio.get_running_loop(), job_id)
                        report("received", "Job picked up by this gpu")
                        try:
                            start_t = time.monotonic()
                            result = await asyncio.to_thread(execute_pipeline_task, forecaster, job_payload, report)
                            duration = time.monotonic() - start_t
                            log.info("Job %s completed in %.2fs. Sending results.", job_id, duration)

                            await websocket.send(
                                json.dumps(
                                    {
                                        "type": "simulation_result",
                                        "job_id": result["job_id"],
                                        "status": "success",
                                        "duration_seconds": duration,
                                        "payload": result,
                                    }
                                )
                            )
                        except requests.exceptions.RequestException as err:
                            # upstream data source failed so gpu not quarentined
                            log.warning("Data source unavailable for %s: %s", job_id, err)
                            await websocket.send(
                                json.dumps(
                                    {
                                        "type": "simulation_error",
                                        "job_id": job_id,
                                        "error": "Upstream data source unavailable",
                                        "error_kind": "data_source"
                                    }
                                )
                        )
                        except Exception as err:
                            log.exception("Task processing error for %s: %s", job_id, err)
                            await websocket.send(
                                json.dumps(
                                    {
                                        "type": "simulation_error",
                                        "job_id": job_id,
                                        "error": "Task execution failure",
                                    }
                                )
                            )

        except websockets.exceptions.InvalidStatus as err:
            status_code = getattr(err.response, "status_code", "Unknown")
            log.warning("Broker rejected connection: HTTP %s (node may be quarantined or deactivated). Retrying in 60 seconds", status_code)
            await asyncio.sleep(60)
        except websockets.exceptions.ConnectionClosed as err:
            if getattr(err.rcvd, "code", None) == 4401:
                log.error("Saved credentials were rejected (worker removed or token invalid). Use 'Reset credentials' in FireAway to get a new setup command.")
                clear_saved_credentials()
                sys.exit(1)
            log.warning("Broker connection dropped (%s). Reconnecting in %ds...", err, RECONNECT_DELAY_SECONDS)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)
        except OSError as err:
            log.warning("Broker connection dropped (%s). Reconnecting in %ds...", err, RECONNECT_DELAY_SECONDS)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)
        except Exception as err:
            log.exception("Unexpected worker error: %s", err)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)


def main():

    passed, gpu_name, vram_mb = run_pre_flight_check()
    if not passed:
        log.error("Hardware qualification failed. Exiting.")
        sys.exit(1)

    credentials = load_saved_credentials()
    if credentials is None:
        if not REGISTRATION_KEY:
            log.error("No saved credentials and no REGISTRATION_KEY set. Get a setup command from FireAway.")
            sys.exit(1)
        credentials = register_worker(REGISTRATION_KEY, gpu_name, vram_mb)
        if not credentials:
            log.error("Registration rejected by broker. Exiting")
            sys.exit(1)
        save_credentials(*credentials)

    jwt_token, worker_id = credentials
    forecaster = load_inference_model()

    asyncio.run(run_worker_loop(forecaster, jwt_token))

if __name__ == "__main__":
    main()