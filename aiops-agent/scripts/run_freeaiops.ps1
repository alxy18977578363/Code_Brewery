$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$launcher = "/mnt/e/December/Desktop/aiops-agent/scripts/run_freeaiops_wsl.sh"
Write-Host "Starting FreeAiOps inside WSL2..."
wsl.exe -d Ubuntu -- bash $launcher
