# Resume Relevance System - Multi-stage Docker Build
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  g++ \
  libffi-dev \
  libssl-dev \
  && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -g 999 appuser && \
  useradd -r -u 999 -g appuser appuser

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_new.txt requirements.txt
COPY requirements-test.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
  pip install -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  FLASK_APP=app.py \
  FLASK_ENV=production \
  PORT=5000

# Install system dependencies for production
RUN apt-get update && apt-get install -y \
  libffi8 \
  libssl3 \
  && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -g 999 appuser && \
  useradd -r -u 999 -g appuser appuser

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p uploads/resumes uploads/job_descriptions data embeddings_cache && \
  chown -R appuser:appuser uploads data embeddings_cache

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command (can be overridden)
CMD ["python", "app_safe.py"]

# Development stage
FROM production as development

# Install development dependencies
USER root
COPY --from=builder /app/requirements-test.txt ./
RUN pip install -r requirements-test.txt

# Switch back to app user
USER appuser

# Set development environment
ENV FLASK_ENV=development \
  FLASK_DEBUG=1

# Command for development
CMD ["python", "app_safe.py"]