@echo off
echo ============================
echo  StudyAI — Dev Server Start
echo ============================

REM Start backend in a new terminal window
start "StudyAI Backend" cmd /k "cd /d %~dp0study-ai\backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Give backend 3 seconds to init
timeout /t 3 /nobreak

REM Start frontend in a new terminal window
start "StudyAI Frontend" cmd /k "cd /d %~dp0study-ai\frontend && python -m streamlit run app.py --server.port 8501 --server.headless true"

echo.
echo Backend:  http://localhost:8000
echo Docs:     http://localhost:8000/docs
echo Frontend: http://localhost:8501
echo.
pause
