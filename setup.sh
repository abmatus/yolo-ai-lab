#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Auto-Installer & Systemd Setup Script for Jetson Orin Nano
# Usage: sudo ./setup.sh
# ==============================================================================

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./setup.sh)"
  exit 1
fi

echo "======================================================================"
echo "      HFU AI-LAB: NVIDIA Jetson Orin Nano Auto-Installer Setup"
echo "======================================================================"

# 1. Install Docker & Docker Compose if missing
if ! command -v docker &> /dev/null; then
    echo "[SETUP] Installing Docker & Docker Compose..."
    apt-get update && apt-get install -y docker.io docker-compose git v4l-utils hostapd dnsmasq curl
    systemctl enable docker
    systemctl start docker
fi

# 2. Add current user to docker group
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker "$SUDO_USER"
    echo "[SETUP] User $SUDO_USER added to docker group."
fi

# 3. Create Systemd Autostart & Auto-Update Service
SERVICE_FILE="/etc/systemd/system/hfu-ai-lab.service"
WORKING_DIR="$(pwd)"

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=HFU AI Workstation Autostart & Auto-Update Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${WORKING_DIR}
ExecStart=/bin/bash ${WORKING_DIR}/scripts/update.sh
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"
systemctl daemon-reload
systemctl enable hfu-ai-lab.service

echo "[SUCCESS] Autostart & Auto-Update Service enabled!"

# 4. Make scripts executable
chmod +x scripts/*.sh

# 5. Run initial startup & container build
bash scripts/update.sh

echo "======================================================================"
echo "[COMPLETE] Setup finished! HFU AI Workstation is ready & active."
echo "Dashboard: http://localhost or http://192.168.4.1"
echo "======================================================================"
