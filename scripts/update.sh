#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Smart Auto-Update & Startup Script
# Checks internet connectivity. Updates from GitHub if online; runs 100% offline otherwise.
# ==============================================================================

echo "======================================================================"
echo "          HFU AI Workstation - System Startup & Auto-Update"
echo "======================================================================"

# 1. Quick network check (2-second timeout to github.com)
echo "[NETWORK CHECK] Testing internet connectivity to GitHub..."
if curl -s --connect-timeout 2 -I https://github.com > /dev/null; then
    ONLINE=true
    echo "[ONLINE MODE] Internet connection detected!"
else
    ONLINE=false
    echo "[OFFLINE MODE] No internet connection detected. Operating in 100% offline mode."
fi

# 2. If Online: Check for updates and pull from GitHub
if [ "$ONLINE" = true ]; then
    echo "[AUTO-UPDATE] Checking for new release on GitHub..."
    git fetch origin main 2>/dev/null
    LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null)
    REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null)

    if [ -n "$LOCAL_HASH" ] && [ -n "$REMOTE_HASH" ] && [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        echo "[AUTO-UPDATE] 🚀 New version found! Pulling updates from GitHub..."
        git pull origin main
        echo "[AUTO-UPDATE] Rebuilding Docker containers with latest update..."
        docker-compose down
        docker-compose up --build -d
        echo "[AUTO-UPDATE] System successfully updated!"
        exit 0
    else
        echo "[AUTO-UPDATE] System is already up to date."
    fi
fi

# 3. Start Docker Containers (Works 100% Offline)
echo "[DOCKER] Ensuring local Docker containers are running..."
docker-compose up -d

echo "======================================================================"
echo "[SUCCESS] HFU AI Workstation is ACTIVE & READY."
echo "Dashboard: http://localhost or http://192.168.4.1"
echo "======================================================================"
