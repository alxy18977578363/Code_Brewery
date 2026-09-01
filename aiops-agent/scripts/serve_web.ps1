$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
Write-Host "AIOps 网页正在启动： http://localhost:5500/web/"
Write-Host "按 Ctrl+C 停止本地服务器。"
python -m http.server 5500
