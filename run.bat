@echo off
cd /d "%~dp0"
call ".venv\Scripts\activate.bat"
cd api
python -m uvicorn app.main:app --host 0.0.0.0 --port 7777
