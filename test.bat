@echo off
call .venv\Scripts\activate.bat
pytest tests/ -v --cov=src
pause