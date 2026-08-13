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

# 1. Install Docker & Prerequisites if missing
echo "[SETUP] Updating package lists and installing prerequisites..."
apt-get update
apt-get install -y git v4l-utils hostapd dnsmasq curl jq docker.io docker-compose-v2 nvidia-container-toolkit || true

# 2. Configure NVIDIA Container Toolkit Runtime
echo "[SETUP] Configuring NVIDIA Container Toolkit & Docker daemon..."
if command -v nvidia-ctk &> /dev/null; then
    nvidia-ctk runtime configure --runtime=docker || true
fi

# Ensure default-runtime is set to nvidia in daemon.json
mkdir -p /etc/docker
if [ -f /etc/docker/daemon.json ]; then
    jq '. + {"default-runtime": "nvidia"}' /etc/docker/daemon.json > /etc/docker/daemon.json.tmp && mv /etc/docker/daemon.json.tmp /etc/docker/daemon.json
else
    cat <<EOF > /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF
fi

systemctl daemon-reload
systemctl restart docker

# 3. Create docker-compose alias/wrapper if missing
if ! command -v docker-compose &> /dev/null; then
    echo "[SETUP] Creating docker-compose wrapper script..."
    cat <<'EOF' > /usr/local/bin/docker-compose
#!/usr/bin/env bash
exec docker compose "$@"
EOF
    chmod +x /usr/local/bin/docker-compose
fi

# 4. Add current user to docker group
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker "$SUDO_USER"
    echo "[SETUP] User $SUDO_USER added to docker group."
fi

# 5. Create Systemd Autostart & Auto-Update Service
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
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"
systemctl daemon-reload
systemctl enable hfu-ai-lab.service

echo "[SUCCESS] Autostart & Auto-Update Service enabled!"

# 6. Make scripts executable
chmod +x scripts/*.sh

# 7. Run initial startup & container build
bash scripts/update.sh

echo "======================================================================"
echo "[COMPLETE] Setup finished! HFU AI Workstation is ready & active."
echo "Dashboard: http://localhost or http://192.168.4.1"
echo "======================================================================"
