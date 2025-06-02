# Backend Dockerfile
#
# This Dockerfile creates the container image for the Flask backend application.
# It uses a slim Python 3.12 image as the base to minimize container size while
# providing all necessary dependencies.

# Start with the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# - unoconv and libreoffice are needed for document generation functionality
RUN apt-get update && apt-get install -y \
    unoconv \
    libreoffice 

# Install Python dependencies
# Copy requirements.txt first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install Gunicorn WSGI server for production deployment
RUN pip install gunicorn

# Copy the entire application code into the container
COPY . .

# Expose port 5000 for the Flask application
# Note: In the docker-compose.yml, this is mapped to port 5001 on the host
EXPOSE 5000

# Run the application using Gunicorn with 4 worker processes
# The application is run via the run.py file that imports the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
