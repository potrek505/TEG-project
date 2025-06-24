FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Install pip and uv
RUN pip install --upgrade pip && pip install uv

# Copy project configuration files first (for better caching)
COPY pyproject.toml ./

# Install dependencies using uv (this layer will be cached if dependencies don't change)
RUN uv pip install . --system

# Copy the rest of the application code
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT:-5000}/health || exit 1

# Start the Flask app
CMD ["python", "app.py"]