# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy package files for installation
COPY cloudMonitoring/ ./cloudMonitoring/
COPY pyproject.toml .
COPY README.md .

# Install only the package with core dependencies (no optional dependencies)
RUN pip install --no-cache-dir .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash monitoring
RUN chown -R monitoring:monitoring /app
USER monitoring

# Set the entrypoint to your package's main module
ENTRYPOINT ["python", "-m", "cloudMonitoring"]

# Default command (can be overridden)
CMD ["--help"]