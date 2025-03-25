@echo off
echo Starting YouTube Downloader Application...

REM Check if we have a virtual environment
if exist venv (
    echo Using virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found, using system Python...
)

REM Run the application
python app.py

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo There was an error starting the application.
    echo Please check if you have installed all required dependencies.
    echo Try running setup.bat first or check the README for instructions.
    pause
) 