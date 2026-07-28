.PHONY: install dev test lint clean run-demo

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --tb=short

test-fast:
	pytest tests/ -v -m "not llm" --tb=short

coverage:
	pytest tests/ --cov=codeslim --cov-report=html

lint:
	ruff check codeslim/ tests/
	mypy codeslim/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ dist/ build/
