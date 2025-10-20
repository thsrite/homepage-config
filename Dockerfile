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

# Run the application
CMD ["python", "run.py"]