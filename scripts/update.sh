#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Auto-Update Script
# Pulls latest updates from GitHub repository and rebuilds Docker containers
# ==============================================================================

echo "[HFU AI-LAB] Checking for updates on GitHub..."

# Fetch & Pull latest changes
git fetch origin main
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    echo "[INFO] New version found on GitHub! Updating..."
    git pull origin main
    
    echo "[INFO] Rebuilding & restarting Docker containers..."
    docker-compose down
    docker-compose up --build -d
    echo "[SUCCESS] HFU AI Workstation successfully updated to latest version!"
else
    echo "[OK] Station is already running the latest version."
fi
