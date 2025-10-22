# Single stage, minimal layers
FROM python:3.11-slim

WORKDIR /app

# Install build dependencies, install Python packages, then clean up
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc g++ libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /app/config /app/uploads && \
    chmod -R 777 /app/config /app/uploads

# Copy all application files in one layer
COPY . .

EXPOSE 9835

CMD ["python", "run.py"]