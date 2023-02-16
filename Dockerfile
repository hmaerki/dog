# syntax=docker/dockerfile:1.4

FROM python:3.14-slim AS builder

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

FROM builder AS dev-envs

RUN pip install --no-cache-dir "."
