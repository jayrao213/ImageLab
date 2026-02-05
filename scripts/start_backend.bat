@echo off
REM PhotoApp Backend Startup Script for Windows

echo ========================================
echo   PhotoApp FastAPI Backend
echo ========================================
echo.

cd ../backend

echo Checking Python installation...
python --version
echo.

echo Installing/Updating dependencies...
pip install -r requirements.txt
echo.

echo Starting FastAPI server...
echo.
echo Server will be available at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
