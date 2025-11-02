@echo off
REM Windows batch script to run the application in development mode

echo Setting up environment...
set DEBUG=True
set PORT=5000
set PYTHONPATH=%CD%

echo Installing dependencies...
pip install -r requirements.txt

echo Starting application...
python app.py