#!/bin/bash
# I-ITSM Startup Script: Launches Backend FastAPI server and Frontend Vite dev server

echo "=========================================================="
echo " Starting Intelligent IT Service Management (I-ITSM) "
echo "=========================================================="

# Ensure Homebrew path is loaded for node / npm if present
if [ -f "/opt/homebrew/bin/brew" ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Activate python virtualenv and start backend
source backend/venv/bin/activate
echo "Starting FastAPI Backend on http://localhost:8000..."
python3 -m uvicorn backend.app.main:app --port 8000 --host 0.0.0.0 --reload &
BACKEND_PID=$!

# Start Vite frontend
echo "Starting Vite Frontend on http://localhost:5173..."
npm --prefix frontend run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo "Both servers running!"
echo "Backend Docs: http://localhost:8000/docs"
echo "Frontend UI:   http://localhost:5173"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
