@echo off

echo "Starting backend (FastAPI) in the background..."
start /B uvicorn main:app --reload

echo "Starting frontend (Vite) in the background..."
pushd frontend
start /B npm run dev
popd

echo.
echo =================================================================
echo.
echo   Backend (FastAPI) and Frontend (Vite) are running.
echo.
echo   Press CTRL+C in this window to stop both servers.
echo.
echo =================================================================
echo.

REM Wait indefinitely until user presses Ctrl+C. This keeps the window open.
timeout /t -1 > nul 