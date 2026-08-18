# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser utils.py .
COPY --chown=appuser:appuser save.json .
COPY --chown=appuser:appuser bids.json .
COPY --chown=appuser:appuser templates/ templates/
COPY --chown=appuser:appuser static/ static/

# Switch to non-root user
USER appuser

# Cloud Run requires the port to be configurable via PORT environment variable
# Default to 8080 (Cloud Run standard)
ENV PORT=8080
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run with gunicorn, binding to 0.0.0.0:$PORT
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 4 --timeout 60 app:app