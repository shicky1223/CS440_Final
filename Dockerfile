FROM ubuntu:22.04

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . .
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]