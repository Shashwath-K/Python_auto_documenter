# Use an official Python runtime as a parent image (slim for smaller size)
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Default port for local use; Koyeb will override this with its own $PORT
ENV PORT 8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    libtk8.6 \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Install Python dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure required directories exist
RUN mkdir -p app/static app/templates

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using the dynamic $PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
