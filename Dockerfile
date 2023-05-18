# Based on https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
# Based on https://github.com/docker/awesome-compose/blob/master/fastapi/Dockerfile
# syntax = docker/dockerfile:1.4

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim AS builder

WORKDIR /app

COPY ./app /app/app

FROM builder as dev-envs

COPY requirements*.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade \
      -r requirements.txt \
      -r requirements_dev.txt

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
