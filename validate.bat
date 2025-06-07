@echo off
call .venv\Scripts\activate.bat
cd src
python symbol_validator.py
cd ..
pause