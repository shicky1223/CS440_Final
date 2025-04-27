# Use an official lightweight Python image
FROM python:3.12-slim

# Don’t buffer stdout/stderr (helpful for logging)
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Copy the rest of your app’s source code
COPY . .

# Expose the port your Flask app runs on
EXPOSE 5000

# Launch the app
# If you’re fine with Flask’s dev server (not recommended for prod):
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# Or, to run your app.py directly:
CMD ["python", "app.py"]
