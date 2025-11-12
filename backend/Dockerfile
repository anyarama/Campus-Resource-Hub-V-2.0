# Backend Dockerfile for Flask Application
# Security: Runs as non-root user

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group
# UID/GID 1000 is typically the first non-system user
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser -m -s /bin/bash appuser

# Copy requirements first for better caching
COPY requirements.txt ./requirements.txt

# Install Python dependencies as root (needed for system-wide installation)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into backend subdirectory to maintain import structure
COPY . ./backend/

# Create necessary directories with proper permissions
RUN mkdir -p backend/instance backend/static/uploads backend/logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    chmod -R 775 backend/instance backend/static/uploads backend/logs

# Set environment variables  
ENV FLASK_APP=backend.app:app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check (runs as appuser)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run server as non-root user
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
