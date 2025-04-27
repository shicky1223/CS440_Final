FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app
ENV FLASK_APP=app.py
EXPOSE 8000
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]