#!/bin/bash

export PYTHONPATH=.

gunicorn -w ${GUNICORN_WORKERS:-"1"} \
  --max-requests ${GUNICORN_WORKER_MAX_REQUESTS:-"10000"} \
  -b :${GUNICORN_PORT:-"8082"} \
  --log-level ${GUNICORN_DEBUG:-"INFO"} \
  -k ${GUNICORN_WORKER_TYPE:-"uvicorn.workers.UvicornWorker"} \
  app:application
