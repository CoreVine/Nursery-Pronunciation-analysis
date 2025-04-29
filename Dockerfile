FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    portaudio19-dev \
    libsndfile1 \
    python3-dev

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create upload directory
RUN mkdir -p uploads && chmod 777 uploads

# Copy the application code
COPY app.py .

# Expose port
EXPOSE 5000

# Run the API using Flask directly (not gunicorn since we removed pygame dependencies)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]