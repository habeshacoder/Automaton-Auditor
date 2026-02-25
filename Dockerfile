FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY rubric/ rubric/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create audit output directory
RUN mkdir -p audit/report_onself_generated

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Entry point
ENTRYPOINT ["python", "-m", "src.main"]
