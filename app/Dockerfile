# flask-app/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy library code first (for better caching)
COPY lib/ /app/lib/

# Copy Flask requirements
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Flask application code
COPY app/ .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with gunicorn for production
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

# For development, use this instead:
CMD ["flask", "run", "app.py"]