# Use slim image for smaller size (pure Python dependencies don't need compilation)
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/config /app/uploads && \
    chmod -R 777 /app/config /app/uploads && \
    # Clean up pip cache
    rm -rf /root/.cache/pip

# Copy only necessary application files
COPY backend ./backend
COPY frontend ./frontend
COPY run.py .

EXPOSE 9835

CMD ["python", "run.py"]