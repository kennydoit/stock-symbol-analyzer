@echo off
call .venv\Scripts\activate.bat
cd src
python symbol_list_generator.py
cd ..
echo.
echo Symbol lists generated! Check the data folder.
pause