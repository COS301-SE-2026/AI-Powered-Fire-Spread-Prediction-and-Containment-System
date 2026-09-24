# to build and run worker container with NVIDIA hardware paas-through
# docker build -t fireaway-worker:latest -f gpu_worker/Dockerfile .
# docker run --gpus all --memory="8g" --memory-swap="8g" -e REGISTRATION_KEY="REG-XXXX" fireaway-worker:latest

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/app \
    UV_HTTP_TIMEOUT=300 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# install libgomp
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libexpat1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN uv venv /opt/venv

# install dependencies
COPY gpu_worker/requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install \
    --index-strategy unsafe-best-match \
    --extra-index-url https://download.pytorch.org/whl/cu128 \
    -r requirements.txt

# copy backend app code
COPY app/__init__.py ./app/__init__.py
COPY app/backend ./app/backend
COPY app/artifact_store ./app/artifact_store

# copy client worker script and model weights
COPY gpu_worker/client_worker.py ./
COPY app/artifact_store/models/weather_convlstm/LATEST/model.pt /app/model/weather_convlstm.pt
ENV MODEL_WEIGHTS_PATH=/app/model/weather_convlstm.pt

CMD ["python", "client_worker.py"]