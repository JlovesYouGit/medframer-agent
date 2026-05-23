@echo off
setlocal

REM Create virtual environment and install dependencies
python -m venv venv
if errorlevel 1 (
  echo Failed to create virtual environment. Ensure Python is installed and on PATH.
  exit /b 1
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
  echo Dependency installation failed.
  exit /b 1
)

echo Virtual environment setup complete. To activate: call venv\Scripts\activate.bat
endlocal
