@echo off
REM PhotoApp Frontend Startup Script for Windows

echo ========================================
echo   PhotoApp Next.js Frontend
echo ========================================
echo.

cd ../frontend

echo Checking Node.js installation...
node --version
echo.

echo Installing/Updating dependencies...
call npm install
echo.

echo Starting Next.js development server...
echo.
echo Frontend will be available at:
echo   - http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
