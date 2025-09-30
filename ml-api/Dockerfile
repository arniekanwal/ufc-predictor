# fast-api/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy library code first (for better caching)
COPY lib/ /app/lib/

# Copy FastAPI requirements
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI application code
COPY ml-api/ .

# Create directory for models if needed
RUN mkdir -p /app/models

# Copy model files (if stored in repo)
COPY models/ /app/models/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run
CMD ["fastapi", "dev", "main.py"]