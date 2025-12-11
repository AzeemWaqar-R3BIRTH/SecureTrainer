# SecureTrainer Production Dockerfile
# Optimized for Render.com deployment

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    FLASK_APP=securetrainer.py

# Set working directory
WORKDIR /app

# Install system dependencies including zbar for QR code scanning
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libzbar0 \
    libzbar-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/model

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:10000/')" || exit 1

# Default command - use gunicorn for production
CMD ["gunicorn", "securetrainer:app", "--bind", "0.0.0.0:10000", "--timeout", "180", "--workers", "1", "--threads", "2"]