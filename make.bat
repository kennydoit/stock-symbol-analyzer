@echo off
REM Windows wrapper for make commands

if "%1"=="" (
    make help
    goto :eof
)

if "%1"=="setup" (
    echo Setting up development environment...
    uv venv
    call .venv\Scripts\activate.bat && uv sync --extra dev --extra jupyter --extra analysis
    echo Environment setup complete!
    goto :eof
)

if "%1"=="validate" (
    echo Running symbol validation...
    cd src && python symbol_validator.py
    goto :eof
)

if "%1"=="screen-momentum" (
    echo Running momentum screening...
    cd workflows && python screening_workflow.py
    goto :eof
)

if "%1"=="test" (
    echo Running tests...
    call .venv\Scripts\activate.bat && pytest tests/ -v --cov=src
    goto :eof
)

if "%1"=="lint" (
    echo Running linting checks...
    call .venv\Scripts\activate.bat && flake8 src/ workflows/ tests/
    call .venv\Scripts\activate.bat && mypy src/ workflows/
    goto :eof
)

if "%1"=="format" (
    echo Formatting code...
    call .venv\Scripts\activate.bat && black src/ workflows/ tests/
    call .venv\Scripts\activate.bat && isort src/ workflows/ tests/
    goto :eof
)

if "%1"=="clean" (
    echo Cleaning up...
    if exist .pytest_cache rmdir /s /q .pytest_cache
    for /r %%i in (__pycache__) do if exist "%%i" rmdir /s /q "%%i"
    for /r %%i in (*.pyc) do if exist "%%i" del /q "%%i"
    goto :eof
)

if "%1"=="jupyter" (
    echo Starting Jupyter Lab...
    call .venv\Scripts\activate.bat && jupyter lab
    goto :eof
)

REM Default: try to run make with the argument
make %1