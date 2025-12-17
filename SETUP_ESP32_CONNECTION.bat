@echo off
echo ========================================
echo ESP32-CAM Connection Setup
echo ========================================
echo.

echo Step 1: Getting your local IP address...
ipconfig | findstr /i "IPv4"
echo.
echo Your server IP should be: 192.168.1.2
echo.

echo Step 2: Starting FastAPI server...
echo Please keep this window open and start the server manually:
echo   cd Server
echo   python main.py
echo.
echo Then open a NEW terminal and run:
echo   python Server\get_jwt_token.py
echo.
pause


