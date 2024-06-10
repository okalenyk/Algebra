# Pull base image
FROM --platform=linux/amd64 python:3.9 as build

# Set environment varibles
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 POETRY_VIRTUALENVS_CREATE=0 SOURCE_DIR=/best_apr_backend WORK_DIR=/code

RUN apt-get update && apt-get upgrade -y && apt-get install -y vim nano

# Set work directory
WORKDIR $WORK_DIR

# Upgrade pip and install poetry
RUN python -m pip install --upgrade pip && pip install poetry

# Copy poetry files
COPY $SOURCE_DIR/poetry.lock $SOURCE_DIR/pyproject.toml $WORK_DIR/

# Install dependencies
RUN poetry install

# Copy project
COPY $SOURCE_DIR/ $WORK_DIR/

ENV BACKEND_SETTINGS_MODE=production BACKEND_DEBUG_MODE=0 APR_DELTA=86400 BLOCK_DELTA=60 DEFAULT_TXN_TIMEOUT=120 DEFAULT_POLL_LATENCY=1
ENV BACKEND_ALLOWED_HOSTS=production=api.kim.finance,localhost,localhost:8081 BACKEND_CSRF_TRUSTED_ORIGINS=api.kim.finance
ENV CORS_ALLOWED_ORIGINS=http://api.kim.finance CORS_ALLOW_METHODS= CORS_ALLOW_CREDENTIALS=0 CORS_ORIGIN_ALLOW_ALL=1

RUN python manage.py collectstatic

# Pull base image
FROM nginx:latest as deploy

# Set environment varibles
ENV WORK_DIR=/etc/nginx/

RUN apt-get update && apt-get upgrade -y && apt-get install -y vim nano

# Set work directory
WORKDIR $WORK_DIR

# Copy static files
COPY --from=build /code/static /usr/share/nginx/static

# Copy confing files
COPY docker/nginx $WORK_DIR