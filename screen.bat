@echo off
call .venv\Scripts\activate.bat
cd workflows
python screening_workflow.py
cd ..
echo.
echo Screening complete! Check the data folder for results.
pause