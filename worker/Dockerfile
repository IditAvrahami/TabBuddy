FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY worker/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY worker/ ./worker/
COPY backend/ ./backend/

# Set Python path
ENV PYTHONPATH=/app

# Run worker
CMD ["python", "-m", "worker.main"]
