# Use official Python image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
ENV PYTHONUNBUFFERED=1
# Set work directory
WORKDIR /home/appuser

# Install system dependencies if needed
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .
RUN mkdir -p /home/appuser/.cache
RUN uv sync --locked
# Expose port (if your app uses one, e.g., Flask/FastAPI)
EXPOSE 8081

# Run the app with Python
CMD ["uv", "run", "main.py", "start"]
