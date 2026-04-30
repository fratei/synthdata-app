# --- Build stage ---
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Production stage ---
FROM python:3.12-slim

LABEL maintainer="CreativeWare <team@creativeware.ai>"
LABEL product="SynthData"

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --create-home app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY src/ ./src/

RUN chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
