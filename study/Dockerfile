FROM node:24-bookworm-slim AS frontend
WORKDIR /frontend
COPY study/frontend/package*.json ./
RUN npm ci
COPY study/frontend/ ./
RUN npm run build

FROM python:3.12-slim AS media
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY study/app/package_videos.py /package_videos.py
COPY videos/homebrew/ /source/
RUN python /package_videos.py /source /videos

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    HOMEBREW_DATA_DIR=/data/homebrew \
    HOMEBREW_VIDEO_DIR=/data/videos/homebrew \
    HOMEBREW_STATIC_DIR=/app/static
WORKDIR /app
RUN pip install --no-cache-dir poetry==2.2.1
COPY study/pyproject.toml study/poetry.lock ./
RUN poetry install --only main --no-root --no-interaction
COPY study/app/ ./app/
COPY data/homebrew/ /data/homebrew/
COPY --from=media /videos/ /data/videos/homebrew/
COPY --from=frontend /frontend/dist/ ./static/
RUN chmod -R a+rX /app/app /app/static /data/homebrew /data/videos \
    && useradd --create-home --uid 10001 reader \
    && mkdir -p /var/lib/homebrew-study \
    && chown reader:reader /var/lib/homebrew-study
USER reader
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
