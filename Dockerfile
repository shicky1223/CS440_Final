FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# <-- tell Docker (and EB) which port you’ll be binding inside the container
EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]