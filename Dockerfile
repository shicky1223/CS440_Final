# Stage 1: Install dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Copy code and dependencies
FROM python:3.12-slim
WORKDIR /app
# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# Copy the rest of your application
COPY . /app

# Expose port and start
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000"]
