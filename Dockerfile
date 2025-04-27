# Stage 1: build dependencies inside a virtualenv

FROM python:3.12-slim AS builder
WORKDIR /app

# Install venv and build tools

RUN apt-get update && apt-get install -y --no-install-recommends python3-venv build-essential && rm -rf /var/lib/apt/lists/*

# Create virtual environment and update PATH

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

Copy and install Python dependencies

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Stage 2: runtime image

FROM python:3.12-slim
WORKDIR /app

Copy virtual environment from builder

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

Copy application code

COPY . /app

Expose port and set entrypoint

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000"]

