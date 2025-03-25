@echo off
echo ===================================
echo   YouTube Downloader Cleanup Script 
echo ===================================

echo.
echo Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1
echo Python cache files removed.

echo.
set /p CONFIRM_MODULES="Do you want to remove node_modules? (y/n): "
if /i "%CONFIRM_MODULES%"=="y" (
    echo Removing node_modules...
    if exist client\node_modules rd /s /q client\node_modules
    echo node_modules removed.
)

echo.
set /p CONFIRM_VENV="Do you want to remove the Python virtual environment (venv)? (y/n): "
if /i "%CONFIRM_VENV%"=="y" (
    echo Removing virtual environment...
    if exist venv rd /s /q venv
    echo Virtual environment removed.
)

echo.
set /p CONFIRM_DOWNLOADS="Do you want to clean the downloads folder? (y/n): "
if /i "%CONFIRM_DOWNLOADS%"=="y" (
    echo Cleaning downloads folder...
    if exist downloads del /q downloads\* >nul 2>&1
    echo Downloads folder cleaned.
)

echo.
echo Cleanup complete! 