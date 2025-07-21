#!/bin/bash

# Запуск бэкенда (FastAPI) в фоне
echo "Запуск бэкенда (FastAPI)..."
uvicorn main:app --reload &
BACKEND_PID=$!

# Запуск фронтенда (Vite) в фоне
cd frontend
echo "Запуск фронтенда (Vite)..."
npm run dev &
FRONTEND_PID=$!
cd ..

# Ожидание завершения обоих процессов
wait $BACKEND_PID $FRONTEND_PID 