#!/usr/bin/env bash
# Run Sentinel-Gate AI Backend and Frontend concurrently

echo "Starting Sentinel-Gate AI Backend..."
python3 -m uvicorn sentinel_gate.backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Starting Sentinel-Gate AI Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "Sentinel-Gate AI running!"
echo "Backend: http://localhost:8000 (Swagger docs at /docs)"
echo "Frontend: http://localhost:3000"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
