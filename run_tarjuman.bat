@echo off
REM Activate virtual environment
call venv\Scripts\activate

REM Navigate to project folder
cd /d E:\ai_projects\Tarjuman

REM Run the FastAPI app
uvicorn Tarjuman.main:app --reload

pause
