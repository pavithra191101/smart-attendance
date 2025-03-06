@echo off
setlocal enabledelayedexpansion

echo Checking Python version...
python --version

echo Upgrading pip...
python -m pip install --upgrade pip

echo Checking if virtual environment exists...
if exist venv (
    echo Virtual environment found. Deleting...
    rmdir /s /q venv
    echo Old virtual environment deleted.
)

echo Creating a new virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Installation failed. Check version compatibility in requirements.txt.
    pause
    exit /b
)

echo Setup complete!
pause
