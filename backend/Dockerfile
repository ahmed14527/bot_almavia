FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    SELENIUM_HEADLESS=true \
    CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Install system dependencies, Chromium, Chromedriver, and PostgreSQL client libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    libpq-dev \
    gcc \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -s /bin/bash -m appuser

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app/

# Ensure entrypoint scripts have Unix executable permissions
RUN chmod +x /app/docker/backend-entrypoint.sh /app/docker/worker-entrypoint.sh

# Create media and static directories and assign ownership to appuser
RUN mkdir -p /app/media/screenshots /app/media/passport_images /app/staticfiles && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/docker/backend-entrypoint.sh"]

CMD ["gunicorn", "visa_bot_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
