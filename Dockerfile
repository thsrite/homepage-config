# Multi-stage build for smaller final image
# Stage 1: Build stage with compilation tools
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create necessary directories with proper permissions
RUN mkdir -p /app/config /app/uploads /app/public/images && \
    chmod -R 777 /app/config /app/uploads /app/public/images

# Copy only necessary application files
COPY backend ./backend
COPY frontend ./frontend
COPY run.py .

EXPOSE 9835

CMD ["python", "run.py"]