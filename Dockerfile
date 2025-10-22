# Use standard Python image instead of slim for better compatibility
FROM python:3.11

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /app/config /app/uploads && \
    chmod -R 777 /app/config /app/uploads

# Copy all application files
COPY . .

EXPOSE 9835

CMD ["python", "run.py"]