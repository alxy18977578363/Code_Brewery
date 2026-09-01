#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="/mnt/e/December/Desktop/aiops-agent"
FREEAIOPS_ROOT="$PROJECT_ROOT/framework/FreeAiOps"
export EWA_CONFIG="$PROJECT_ROOT/config.freeaiops.local.yaml"

cd "$FREEAIOPS_ROOT"
echo "FreeAiOps WSL2: http://127.0.0.1:8080/"
echo "Health: http://127.0.0.1:8080/health"
echo "Running FreeAiOps database migration..."
go run ./cmd/migrate
exec go run ./cmd
