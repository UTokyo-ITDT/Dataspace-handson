# EDC Simple UI - Dockerfile
FROM python:3.12-slim AS runtime
# ※ pyproject.toml に合わせて 3.12 を推奨（3.11 のままでも動けば可）

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install minimal system tools
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# 非rootユーザ
RUN addgroup --system app \
 && adduser  --system --ingroup app --home /home/app app \
 && mkdir -p /home/app/.config /home/app/.cache \
 && chown -R app:app /home/app

WORKDIR /app

# 依存だけ先にコピー→インストール（キャッシュ効く）
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r /app/requirements.txt

# アプリ本体
COPY --chown=app:app . /app
USER app

CMD ["python", "-c", "print('Container built. Override CMD in docker-compose.yml')"]