# Sentinel-Gate AI: Windows Local Startup Script

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting Sentinel-Gate AI Services" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Start Backend in background or separate window
Start-Process python -ArgumentList "-m", "uvicorn", "sentinel_gate.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"

Write-Host "Backend started at http://localhost:8000" -ForegroundColor Green
Write-Host "Interactive Swagger Docs available at http://localhost:8000/docs" -ForegroundColor Green

# Start Frontend
Set-Location frontend
Write-Host "Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Cyan
npm run dev
