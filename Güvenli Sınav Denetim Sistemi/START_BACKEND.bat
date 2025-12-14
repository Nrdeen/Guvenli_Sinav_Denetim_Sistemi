@echo off
echo ========================================
echo   Guvenli Sinav - Backend API Server
echo ========================================
echo.

cd /d "%~dp0backend"

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Starting FastAPI Server on http://localhost:8001
echo.
echo Press CTRL+C to stop the server
echo.

python main.py

pause
