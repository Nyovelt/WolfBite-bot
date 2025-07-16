# Use official Python 3.10 image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install git to pull the repository
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the repository into the working directory
COPY . . 

# Ensure the repository is always up to date whenever the container starts
RUN git pull origin main && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
