.PHONY: install dev test lint seed

install:
	python -m pip install -r requirements-dev.txt

dev:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

test:
	python -m unittest discover -s tests -v

lint:
	ruff check backend tests scripts

seed:
	python scripts/generate_data.py

