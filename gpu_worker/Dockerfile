# to build and run worker container with NVIDIA hardware paas-through
# docker build -t fireaway-worker:latest -f gpu_worker/Dockerfile .
# docker run --gpus all --memory="8g" --memory-swap="8g" -e REGISTRATION_KEY="REG-XXXX" fireaway-worker:latest

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

COPY gpu_worker/requirements.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --only-binary :all: \
    -r requirements.txt

COPY gpu_worker/client_worker.py ./
COPY app/artifact_store/models/weather_convlstm/LATEST/model.pt /app/model/weather_convlstm.pt
ENV MODEL_WEIGHTS_PATH=/app/model/weather_convlstm.pt

CMD ["python", "client_worker.py"]