FROM python:3.10.13-slim

# ── Environment Variables ─────────────────────────────────────────────────────
# Prevent Python from writing .pyc files
# Force Python to flush stdout/stderr streams (useful for logging)
# Disable pip cache to reduce image size
# Prevent pip from checking for updates
# Add /app to PYTHONPATH so Django apps can be imported from anywhere
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# ── System Dependencies ───────────────────────────────────────────────────────
# Install essential build tools, PostgreSQL client libraries, netcat for service checks, and bash
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev netcat-openbsd bash \
 && rm -rf /var/lib/apt/lists/*

# ── Set Working Directory ─────────────────────────────────────────────────────
# Define /app as the working directory for the application
WORKDIR /app

# ── Install Python Dependencies ───────────────────────────────────────────────
# Copy requirements file and install Python packages without cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Application Code ─────────────────────────────────────────────────────
COPY . .

# ── Verify Code is Copied ─────────────────────────────────────────────────────
# Sanity check: list contents and verify manage.py exists
RUN ls -la /app | head -n 100 && test -f /app/manage.py

# ── Entrypoint Script ─────────────────────────────────────────────────────────
# Copy entrypoint, remove CRLF if present (for Windows compatibility), and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# ── Port Exposure ─────────────────────────────────────────────────────────────
# Expose port 8000 for the web server (Gunicorn)
EXPOSE 8000

# ── Default Entrypoint ────────────────────────────────────────────────────────
ENTRYPOINT ["/entrypoint.sh"]

