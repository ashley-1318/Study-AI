@echo off
echo 🚀 Starting StudyAI Project...

:: Start Backend
start "StudyAI Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: Start Frontend
start "StudyAI Frontend" cmd /k "cd frontend && python -m streamlit run app.py --server.port 8501"

echo ✅ Both services are starting in separate windows.
echo 🌐 Backend: http://localhost:8000
echo 🌐 Frontend: http://localhost:8501
pause
