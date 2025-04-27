FROM ubuntu:22.04

# install Python3 + pip3
RUN apt-get update \
 && apt-get install -y python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Set your app folder
WORKDIR /app

# If you have other libraries, include a requirements.txt
# COPY requirements.txt .
# RUN pip3 install --no-cache-dir -r requirements.txt

# Flask itself (and any others you might need)
RUN pip3 install flask==3.0.*

# Copy in your app code
COPY app.py .

# Tell Flask which file to load
ENV FLASK_APP=app

# Expose the port you run on
# EXPOSE 8000

# Use python3 & the flask CLI
CMD ["python3", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "8000"]
