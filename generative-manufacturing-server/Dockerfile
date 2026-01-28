FROM python:3.11-slim-bookworm

# Install system dependencies
# openscad and prusa-slicer are needed for the core functionality
# libgl1-mesa-glx is often required for these tools even in headless mode
RUN apt-get update && apt-get install -y \
    openscad \
    prusa-slicer \
    libgl1-mesa-glx \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Explicitly set paths, though they should be in PATH
ENV OPENSCAD_PATH=/usr/bin/openscad
ENV PRUSA_SLICER_PATH=/usr/bin/prusa-slicer

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port (Cloud Run defaults to 8080, but MCP over SSE might vary)
# Assuming the server listens on PORT env var or a default
ENV PORT=8080

# Command to run the application
# Using 'uv run' ensures the virtual environment is used
CMD ["uv", "run", "server.py"]
