FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Coqui TTS license agreement
ENV COQUI_TOS_AGREED=1

# Copy application files
COPY app.py ./app.py
COPY download_model.py ./download_model.py

# Pre-download the TTS model during build to reduce first request latency
RUN python download_model.py

# Render provides $PORT; default to 8000 locally
ENV PORT=8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["sh","-c","uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
