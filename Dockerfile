FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies needed for scientific libs and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libfreetype6-dev \
    libpng-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs static/uploads static/images

# Expose port and set defaults
ENV PORT=5000 \
    DEBUG=False \
    PYTHONPATH=/app
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=5 \
    CMD curl -fsS http://localhost:${PORT}/api/health || exit 1

# Run using gunicorn for production
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
