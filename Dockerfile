# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 homepage && \
    mkdir -p /app/configs /app/uploads && \
    chown -R homepage:homepage /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/homepage/.local

# Copy application files
COPY --chown=homepage:homepage backend/ ./backend/
COPY --chown=homepage:homepage frontend/ ./frontend/
COPY --chown=homepage:homepage run.py .
COPY --chown=homepage:homepage requirements.txt .

# Switch to non-root user
USER homepage

# Add user's local bin to PATH
ENV PATH=/home/homepage/.local/bin:$PATH

# Expose port
EXPOSE 9835

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; exit(0 if requests.get('http://localhost:9835/health').status_code == 200 else 1)" || exit 1

# Run the application
CMD ["python", "run.py"]