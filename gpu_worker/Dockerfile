# to build and run worker container with NVIDIA hardware paas-through
# docker build -t fireaway-worker:latest -f gpu_worker/Dockerfile gpu_worker/
# docker run --gpus all --memory="8g" --memory-swap="8g" -e REGISTRATION_KEY="REG-XXXX" fireaway-worker:latest

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirments.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY client_worker.py ./

CMD ["python", "client_worker.py"]