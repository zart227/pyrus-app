@echo off
setlocal

REM --- Backend Setup ---
echo --- Setting up Python backend ---

REM Check for python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo python could not be found. Please install Python.
    goto :eof
)

REM Create a virtual environment
echo Creating Python virtual environment in '.venv'...
python -m venv .venv

REM Activate the virtual environment and install dependencies
echo Installing backend dependencies from requirements.txt...
call .venv\Scripts\activate.bat
pip install -r requirements.txt
call .venv\Scripts\deactivate.bat

echo Backend setup complete.
echo.

REM --- Frontend Setup ---
echo --- Setting up Node.js frontend ---

REM Check for npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo npm could not be found. Please install Node.js and npm.
    goto :eof
)

REM Install frontend dependencies
if exist "frontend" (
  echo Navigating to 'frontend' directory...
  pushd frontend
  echo Installing frontend dependencies with npm...
  npm install
  popd
) else (
  echo Warning: 'frontend' directory not found. Skipping frontend setup.
)

echo Frontend setup complete.
echo.
echo Setup finished successfully!
echo Run 'start.sh' (on Linux/macOS) or 'start.bat' (on Windows) to start the servers.

endlocal 