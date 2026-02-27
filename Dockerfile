FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata and code
COPY pyproject.toml .
COPY src/ src/
COPY rubric/ rubric/

# Install Python deps (editable install)
RUN pip install --no-cache-dir -e .

# Ensure audit output dir exists (matches Config.AUDIT_OUTPUT_DIR)
RUN mkdir -p audit/report_onself_generated

# Runtime env
ENV PYTHONUNBUFFERED=1

# Entry point (args come from docker-compose)
ENTRYPOINT ["python", "-m", "src.main"]
