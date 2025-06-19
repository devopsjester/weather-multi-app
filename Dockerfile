FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash weatherapp
USER weatherapp

# Expose ports for web interface
EXPOSE 5000

# Default command
CMD ["python", "-m", "weather_app", "web", "--host", "0.0.0.0", "--port", "5000"]

# Labels
LABEL org.opencontainers.image.title="Weather Multi-App"
LABEL org.opencontainers.image.description="A comprehensive weather application with CLI, Web, and MCP interfaces"
LABEL org.opencontainers.image.source="https://github.com/devopsjester/weather-multi-app"
LABEL org.opencontainers.image.licenses="MIT"
