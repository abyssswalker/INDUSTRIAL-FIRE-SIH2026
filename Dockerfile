# Use the official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# The Hackathon Lifesaver: Install system-level geospatial C-libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables so Python can find them
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy your requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your actual FastAPI code into the container
COPY . .

# Expose the port Render uses
EXPOSE 10000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
