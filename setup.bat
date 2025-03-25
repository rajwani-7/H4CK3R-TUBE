@echo off
echo ====================================
echo   YouTube Downloader Setup Script   
echo ====================================

echo.
echo Checking for Python...
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please install Python 3.6+ and try again.
    exit /b 1
) else (
    echo Python is installed!
)

echo.
echo Checking for Node.js and npm...
where node >nul 2>&1 && where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Node.js and/or npm are not installed. Please install Node.js 14+ and npm 6+ and try again.
    exit /b 1
) else (
    echo Node.js and npm are installed!
    for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
    for /f "tokens=*" %%i in ('npm -v') do set NPM_VERSION=%%i
    echo Node.js version: %NODE_VERSION%
    echo npm version: %NPM_VERSION%
)

echo.
echo Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Installing backend dependencies...
pip install -r requirements.txt

echo.
echo Installing frontend dependencies...
cd client && npm install
cd ..

echo.
echo Creating downloads directory...
if not exist downloads mkdir downloads

echo.
echo Downloading assets (sounds and favicon)...
call download_sounds.bat
call download_favicon.bat

echo.
echo Setup complete!

echo.
echo To run the application:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Start the application: python app.py
echo   - Or use the start_app.bat script
echo.
echo The application will be available at: http://localhost:5000 