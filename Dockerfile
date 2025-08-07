# Use official Python image
# FROM python:3.11-slim

# Set work directory
WORKDIR /

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port if your app listens on a port (optional, for web apps)
# EXPOSE 8000

# Set environment variables (optional, for production best practice)
# ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
