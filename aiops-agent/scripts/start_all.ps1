$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$freeAiOpsRootLinux = "/mnt/e/December/Desktop/aiops-agent/framework/FreeAiOps"
$configLinux = "/mnt/e/December/Desktop/aiops-agent/config.freeaiops.local.yaml"

function Test-HttpOk([string]$Url) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri $Url
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 300
    } catch {
        return $false
    }
}

function Get-WslIp {
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $raw = wsl.exe -d Ubuntu -- hostname -I 2>$null
    $ErrorActionPreference = $oldPreference
    return ($raw -split "\s+" | Where-Object { $_ -match '^\d+\.\d+\.\d+\.\d+$' } | Select-Object -First 1)
}

Write-Host "=== AIOps Agent startup ===" -ForegroundColor Cyan
Set-Location $projectRoot

$dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
try { docker info --format "{{.ServerVersion}}" *> $null } catch { $LASTEXITCODE = 1 }
if ($LASTEXITCODE -ne 0) {
    if (-not (Test-Path -LiteralPath $dockerDesktop)) { throw "Docker Desktop not found: $dockerDesktop" }
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process -FilePath $dockerDesktop
    $dockerReady = $false
    for ($i = 0; $i -lt 24; $i++) {
        Start-Sleep -Seconds 5
        docker info --format "{{.ServerVersion}}" *> $null
        if ($LASTEXITCODE -eq 0) { $dockerReady = $true; break }
    }
    if (-not $dockerReady) { throw "Docker Desktop did not become ready within 120 seconds." }
}
Write-Host "Docker engine: ready" -ForegroundColor Green

Write-Host "Starting Demo service and MySQL..." -ForegroundColor Yellow
docker compose up -d --build
docker compose ps
if (-not (Test-HttpOk "http://127.0.0.1:9000/health")) { throw "Demo service health check failed." }
Write-Host "Demo service: online (9000)" -ForegroundColor Green

$wslIp = Get-WslIp
$freeAiOpsOnline = $false
if ($wslIp) { $freeAiOpsOnline = Test-HttpOk "http://${wslIp}:8080/health" }
if (-not $freeAiOpsOnline) {
    Write-Host "Starting FreeAiOps in WSL2..." -ForegroundColor Yellow
    $launcherLinux = "/mnt/e/December/Desktop/aiops-agent/scripts/run_freeaiops_wsl.sh"
    # Keep the Bash script in a file instead of embedding `export` in a
    # PowerShell command. This avoids PowerShell interpreting Linux syntax.
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "wsl.exe -d Ubuntu -- bash $launcherLinux")
    for ($i = 0; $i -lt 24; $i++) {
        Start-Sleep -Seconds 5
        $wslIp = Get-WslIp
        if ($wslIp -and (Test-HttpOk "http://${wslIp}:8080/health")) { $freeAiOpsOnline = $true; break }
    }
}
if (-not $freeAiOpsOnline) { throw "FreeAiOps health check failed." }
Write-Host "FreeAiOps: online (WSL2 ${wslIp}:8080)" -ForegroundColor Green

if (-not (Test-HttpOk "http://127.0.0.1:8000/api/health")) {
    Write-Host "Starting Agent API..." -ForegroundColor Yellow
    $apiScript = Join-Path $projectRoot "scripts\run_api.ps1"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $apiScript)
    $apiReady = $false
    for ($i = 0; $i -lt 18; $i++) {
        Start-Sleep -Seconds 2
        if (Test-HttpOk "http://127.0.0.1:8000/api/health") { $apiReady = $true; break }
    }
    if (-not $apiReady) { throw "Agent API health check failed." }
}
Write-Host "Agent API: online (8000)" -ForegroundColor Green

$agentStatus = Invoke-RestMethod "http://127.0.0.1:8000/api/freeaiops/status"
Write-Host ""
Write-Host "=== Startup complete ===" -ForegroundColor Cyan
Write-Host "Dashboard:  http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "API docs:   http://127.0.0.1:8000/docs"
Write-Host "Demo:       http://127.0.0.1:9000/health"
Write-Host "FreeAiOps:  http://${wslIp}:8080/health"
Write-Host "FreeAiOps status: $($agentStatus.status)" -ForegroundColor Green
Write-Host "Keep the FreeAiOps and Agent API windows open." -ForegroundColor Yellow
