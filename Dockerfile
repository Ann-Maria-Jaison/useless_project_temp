FROM python:3.10-slim

# Install system dependencies (espeak for pyttsx3 voice synthesis)
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak \
    libespeak1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Set environment variables
ENV PORT=5000 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# Run with Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]
