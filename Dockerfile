# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install only what's needed - no build tools required for pure Python packages
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /usr/local

# Copy application files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY run.py .
COPY requirements.txt .
COPY entrypoint.sh .

# Create directories and set entrypoint permissions
RUN mkdir -p /app/configs /app/uploads && \
    chmod -R 777 /app/configs /app/uploads && \
    chmod +x entrypoint.sh

# Expose port
EXPOSE 9835

# Use entrypoint to handle permissions
ENTRYPOINT ["/app/entrypoint.sh"]