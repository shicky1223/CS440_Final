# Stage 1: install dependencies

FROM python:3.12-slim AS builder
WORKDIR /app

Copy and install python dependencies

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Stage 2: build runtime image

FROM python:3.12-slim
WORKDIR /app

Copy installed packages from builder

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

Copy application code

COPY . /app

Expose port and set entrypoint

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000"]

