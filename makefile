# Makefile for your Flask chat application

.PHONY: help install run gunicorn clean

help:
	@echo "Usage:"
	@echo "  make install     Install Python dependencies"
	@echo "  make run         Run dev server (Flask)"
	@echo "  make gunicorn    Run prod server (Gunicorn)"
	@echo "  make clean       Remove Python cache files"

install:
	pip install -r requirements.txt

run:
	# load .env automatically via python-dotenv
	export FLASK_APP=app.py
	export FLASK_ENV=development
	flask run --host=0.0.0.0 --port=8000

gunicorn:
	# WSGI entrypoint is application in app.py
	gunicorn app:application --bind 0.0.0.0:$(PORT) \
	--workers 4 --threads 2 --preload

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
