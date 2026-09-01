$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$env:DEMO_SERVICE_BASE_URL = "http://127.0.0.1:9000"
$savedErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$wslRaw = wsl.exe -d Ubuntu -- hostname -I 2>$null
$ErrorActionPreference = $savedErrorActionPreference
$wslIp = $wslRaw -split '\s+' | Where-Object { $_ -match '^\d+\.\d+\.\d+\.\d+$' } | Select-Object -First 1
if ($wslIp) { $env:FREEAIOPS_BASE_URL = "http://$wslIp`:8080"; Write-Host "FreeAiOps health target: $env:FREEAIOPS_BASE_URL/health" }
Write-Host "AIOps dashboard: http://127.0.0.1:8000/"
Write-Host "API docs (development only): http://127.0.0.1:8000/docs"
Write-Host "Press Ctrl+C to stop the local service."
python -m uvicorn src.api_server:app --host 127.0.0.1 --port 8000
