
@echo off
cd /d "%~dp0"
cd api
call "%~dp0.venv\Scripts\activate.bat"
python -m uvicorn app.main:app --host 0.0.0.0 --port 7777