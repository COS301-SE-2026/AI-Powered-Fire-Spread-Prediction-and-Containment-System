# Polls fire-system-gpu-inference for jobs, runs the fire-spread model and publishes the results to fire-system-gpu-results

import json
import logging
import os
import time
from pathlib import Path

import boto3

from app.backend.src.ai.dca import run_dca

AWS_REGION = os.environ["AWS_REGION"]
INFERENCE_QUEUE_URL = os.environ["INFERENCE_QUEUE_URL"]
RESULTS_QUEUE_URL = os.environ["RESULTS_QUEUE_URL"]

WORKER_ID = os.environ.get("WORKER_ID", "gpu-worker-1")

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
VISIBILITY_TIMEOUT_SECONDS = 60

sqs = boto3.client("sqs", region_name=AWS_REGION)


def run_inference(job: dict) -> dict:
    # Need to put model call here
    # 'job' is whatever payload app side published to fire-system-gpu-inference.
    # Must return a JSON-serializable dict. Needs enough identifying info (min 'job_id' and 'region_id')so backend's results-consumer background task can key result correctly in Valkey

    job_id = job["job_id"]
    region_id = job["region_id"]

    weather_grids = {
        "wind_u": job["weather"]["wind_u"],
        "wind_v": job["weather"]["wind_v"],
        "rel_humidity": job["weather"]["rel_humidity"],
        "temperature": job["weather"]["temperature"],
    }

    static_grids = {
        "elevation": job["static"]["elevation"],
        "slope": job["static"]["slope"],
        "aspect_sin": job["static"]["aspect_sin"],
        "aspect_cos": job["static"]["aspect_cos"],
        "fuel_load": job["static"]["fuel_load"],
        "dryness": job["static"]["dryness"],
    }

    n_steps = job.get("steps", 100)
    n_ignition_points = job.get("n_ignition_points", 1)

    history = run_dca(
        weather_grids,
        static_grids,
        n_steps=n_steps,
        n_ignition_points=n_ignition_points,
    )

    return {
        "job_id": job_id,
        "region_id": region_id,
        "history": [grid.tolist() for grid in history],
    }


def touch_heartbeat() -> None:
    HEARTBEAT_FILE.write_text(str(time.time()))


def handle_message(message: dict) -> None:
    body = json.loads(message["Body"])
    job_id = body.get("job_id", "<unknown>")
    log.info("Processing job %s", job_id)

    result = run_inference(body)

    sqs.send_message(
        QueueUrl=RESULTS_QUEUE_URL,
        MessageBody=json.dumps(result),
    )
    log.info("Published result for job %s", job_id)

    sqs.delete_message(
        QueueURL=INFERENCE_QUEUE_URL,
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
