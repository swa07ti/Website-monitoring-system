FROM python:3.10-slim

WORKDIR /app

# Copy and install dependencies first (caches this layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files (including monitor.py and the templates/ folder)
COPY . .

# Expose the port for the FastAPI web server
EXPOSE 8000

# Run the monitoring app
CMD ["python", "monitor.py"]
