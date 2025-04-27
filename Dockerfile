# ─── Base image ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# ─── Set working directory ────────────────────────────────────────────────────
WORKDIR /app

# ─── Install dependencies ─────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Copy application code ────────────────────────────────────────────────────
COPY . .

# ─── Environment & port ───────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1

# Expose the port your Flask app runs on (default 5000)
EXPOSE 5000

# ─── Run the app ───────────────────────────────────────────────────────────────
# If you have gunicorn in your requirements, you can do:
#   CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
#
# Otherwise for simple development:
CMD ["python", "app.py"]
