@echo off
call .venv\Scripts\activate.bat
black src/ workflows/ tests/
isort src/ workflows/ tests/
echo Code formatting complete!
pause