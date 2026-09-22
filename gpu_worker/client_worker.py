# for volunteer gpus
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from typing import Optional, Tuple

import numpy as np
import requests
import torch
import websockets

from app.backend.ml.models.nowcast_model import WeatherDeltaModel
from app.backend.src.ai.model_pipeline import run_convlstm_dca
from app.backend.src.ai.simulation import build_boundary_ignition_mask
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
MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", "app/cached/ml/models/weather_convlstm.pt")

MIN_VRAM_MB = 4096
BENCHMARK_DURATION_SECONDS = 1.0
RECONNECT_DELAY_SECONDS = 5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


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


def load_inference_model() -> WeatherDeltaModel:
    model = WeatherDeltaModel()
    if os.path.exists(MODEL_WEIGHTS_PATH):
        try:
            checkpoint = torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE)
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint
            model.load_state_dict(state_dict)
            log.info("Loaded custom model checkpoint from %s", MODEL_WEIGHTS_PATH)
        except Exception as err:
            log.warning("COuld not load weights from %s (%s). Using initialised head.", MODEL_WEIGHTS_PATH, err)
    else:
        log.warning("Weights path %s not found. Using zero-initialised model head.", MODEL_WEIGHTS_PATH)

    model.to(DEVICE)
    model.eval()
    return model


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


def execute_pipeline_task(model: WeatherDeltaModel, payload: dict) -> dict:
    job_id = payload.get("job_id", "sim_task")
    log.info("Fetching remote terrain and weather data for job: %s", job_id)

    # fetch satelite and weather data
    weather_history = fetch_weather_history(payload)
    static_grids = fetch_static_grids(payload)

    # build the [1 T 4 H W] tensor for lstm
    frames = []
    for frame in weather_history:
        stacked = np.stack(
            [
                frame["wind_u"],
                frame["wind_v"],
                frame["rel_humidity"],
                frame["temperature"]
            ],
            axis=0
        ).astype(np.float32)
        frames.append(stacked)
    weather_tensor = torch.from_numpy(np.stack(frames, axis=0)).unsqueeze(0)

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

    history = run_convlstm_dca(
        convlstm_model=model,
        weather_history=weather_tensor,
        static_grids=static_grids,
        cell_size_m=payload["cell_size_m"],
        n_steps=payload["n_steps"],
        ignition_mask=ignition_mask,
        containment_lines=payload.get("containment_lines"),
        grid_bounds=payload.get("grid_bounds"),
        params=params,
    )

    history_list = [grid.tolist() for grid in history]

    return {
        "job_id": job_id,
        "status": "completed",
        "history": history_list,
    }

async def run_worker_loop(model: WeatherDeltaModel, worker_jwt: str):
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
                        try:
                            start_t = time.monotonic()
                            result = execute_pipeline_task(model, job_payload)
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
            log.error("Authentication rejected: HTTP %s (%s)", status_code, err)
            return
        except (websockets.exceptions.ConnectionClosed, OSError) as err:
            log.warning("Broker connection dropped (%s). Reconnecting in %ds...", err, RECONNECT_DELAY_SECONDS)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)
        except Exception as err:
            log.exception("Unexpected worker error: %s", err)
            await asyncio.sleep(RECONNECT_DELAY_SECONDS)


def main():
    if not REGISTRATION_KEY:
        log.error("Missing REGISTRATION_KEY environment variable. Terminating.")
        sys.exit(1)

    passed, gpu_name, vram_mb = run_pre_flight_check()
    if not passed:
        log.error("Hardware qualification failed. Exiting.")
        sys.exit(1)

    registration_result = register_worker(REGISTRATION_KEY, gpu_name, vram_mb)
    if not registration_result:
        log.error("Registration rejected by broker. Exiting.")
        sys.exit(1)

    jwt_token, worker_id = registration_result
    model = load_inference_model()

    asyncio.run(run_worker_loop(model, jwt_token))

if __name__ == "__main__":
    main()