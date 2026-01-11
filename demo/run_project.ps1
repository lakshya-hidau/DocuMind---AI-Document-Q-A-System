Write-Host "Installing Backend Dependencies..."
python -m pip install -r backend/requirements.txt

Write-Host "Starting Backend Server..."
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.main:app --reload --port 8000" -PassThru -WindowStyle Minimized

Write-Host "Backend started with PID: $($backendProcess.Id)"
Write-Host "Starting Frontend Server..."

Set-Location frontend
# Using direct node execution to avoid issues with spaces in path
node node_modules/vite/bin/vite.js
