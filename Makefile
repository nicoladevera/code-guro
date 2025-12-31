.PHONY: help install format lint test quality clean samples

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in development mode with all dependencies
	pip install -e ".[dev]"
	pre-commit install

format:  ## Format code with Black
	black src/

lint:  ## Check code with Ruff (and auto-fix)
	ruff check src/ --fix

test:  ## Run tests with pytest
	pytest

quality: format lint test  ## Run all quality checks (format, lint, test)
	@echo "✅ All quality checks passed!"

pre-commit:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean:  ## Clean up cache and build files
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type d -name .pytest_cache -exec rm -r {} +
	find . -type d -name .ruff_cache -exec rm -r {} +
	find . -type f -name '*.pyc' -delete

samples:  ## Generate HTML from sample markdown files
	@mkdir -p samples/html
	python3 -c "from pathlib import Path; from code_guro.html_converter import convert_directory_to_html_organized; convert_directory_to_html_organized(Path('samples/markdown'), Path('samples/html'))"
	@echo "✅ Sample HTML files generated in samples/html/"
