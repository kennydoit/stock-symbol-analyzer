# Stock Symbol Analyzer Makefile
.PHONY: help install validate screen-momentum test lint format clean setup

# Default target
help:
    @echo "Available commands:"
    @echo "  setup           - Set up the development environment"
    @echo "  install         - Install dependencies with uv"
    @echo "  validate        - Run symbol validation"
    @echo "  screen-momentum - Run momentum screening"
    @echo "  test           - Run tests"
    @echo "  lint           - Run linting checks"
    @echo "  format         - Format code with black and isort"
    @echo "  clean          - Clean up generated files"
    @echo "  all            - Run validation and screening"

# Environment setup
setup:
    @echo "Setting up development environment..."
    uv venv
    .venv\Scripts\activate && uv sync --extra dev --extra jupyter
    @echo "Environment setup complete!"

install:
    @echo "Installing dependencies..."
    uv sync --extra dev --extra jupyter --extra analysis

# Core workflows
validate:
    @echo "Running symbol validation..."
    cd src && python symbol_validator.py

screen-momentum:
    @echo "Running momentum screening..."
    cd workflows && python screening_workflow.py

# Development tools
test:
    @echo "Running tests..."
    pytest tests/ -v --cov=src

lint:
    @echo "Running linting checks..."
    flake8 src/ workflows/ tests/
    mypy src/ workflows/

format:
    @echo "Formatting code..."
    black src/ workflows/ tests/
    isort src/ workflows/ tests/

# Utility targets
clean:
    @echo "Cleaning up..."
    rmdir /s /q .pytest_cache 2>nul || echo "No pytest cache to clean"
    rmdir /s /q __pycache__ 2>nul || echo "No pycache to clean"
    del /q *.pyc 2>nul || echo "No .pyc files to clean"

# Combined workflows
all: validate screen-momentum
    @echo "All workflows completed!"

# Data management
refresh-data: validate
    @echo "Data refresh completed!"

# Jupyter setup
jupyter:
    @echo "Starting Jupyter Lab..."
    .venv\Scripts\activate && jupyter lab