# Use Python 3.8 as the base image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for psycopg2, MongoDB, and logging
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files to the working directory
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8574

# Command to run the application
CMD ["python", "serverLog.py"]
