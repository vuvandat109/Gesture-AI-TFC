FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    PORT=5000

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install -r requirements.txt

COPY . .

RUN python scripts/verify_tfc_release.py \
    && useradd --uid 10001 --create-home appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data

ENV DATABASE_PATH=/data/users.db

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import json,urllib.request; d=json.load(urllib.request.urlopen('http://127.0.0.1:5000/api/health',timeout=5)); assert d['model_ready'] and 'TF-C' in d['model']"

CMD ["sh", "-c", "exec python -m gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 2 --timeout 120"]