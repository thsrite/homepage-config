# Single stage, minimal layers
FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies in one layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/config /app/uploads && \
    chmod -R 777 /app/config /app/uploads

# Copy all application files in one layer
COPY . .

EXPOSE 9835

CMD ["python", "run.py"]