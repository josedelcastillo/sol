.PHONY: install test lint run

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest --cov=app --cov-fail-under=80

lint:
	ruff check .

run:
	uvicorn app.main:app --reload --port 8000
