# Backend Dockerfile for Flask Application

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into backend subdirectory to maintain import structure
COPY . ./backend/

# Create necessary directories
RUN mkdir -p backend/instance backend/static/uploads

# Set environment variables  
ENV FLASK_APP=backend.app:app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run server directly (skip migrations for now)
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
