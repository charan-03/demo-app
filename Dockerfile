# Use an official Python runtime as a parent image
FROM python:3.9-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install build dependencies and upgrade pip/setuptools for more robust installs
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    pip install --no-cache-dir --upgrade pip setuptools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the application
# We'll use Gunicorn for a production-ready server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
