#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Auto-Installer & Systemd Setup Script for Jetson Orin Nano
# Usage: sudo bash setup.sh
# ==============================================================================

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo bash setup.sh)"
  exit 1
fi

REAL_USER="${SUDO_USER:-nvidia}"

echo "======================================================================"
echo "      HFU AI-LAB: NVIDIA Jetson Orin Nano Auto-Installer Setup"
echo "======================================================================"

# 1. Update & Upgrade system packages
echo "[SETUP] Updating package lists and upgrading system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y git v4l-utils hostapd dnsmasq curl jq docker.io docker-compose-v2 nvidia-container-toolkit chromium-browser || true

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
usermod -aG docker "$REAL_USER"
echo "[SETUP] User $REAL_USER added to docker group."

# 5. Enable Ubuntu Desktop Auto-Login for $REAL_USER
echo "[SETUP] Enabling Desktop Auto-Login for user $REAL_USER..."
if [ -f /etc/gdm3/custom.conf ]; then
    sed -i 's/^#  AutomaticLoginEnable = .*/AutomaticLoginEnable = true/' /etc/gdm3/custom.conf
    sed -i "s/^#  AutomaticLogin = .*/AutomaticLogin = $REAL_USER/" /etc/gdm3/custom.conf
fi

if [ -d /etc/lightdm ]; then
    mkdir -p /etc/lightdm/lightdm.conf.d
    cat <<EOF > /etc/lightdm/lightdm.conf.d/50-autologin.conf
[Seat:*]
autologin-user=$REAL_USER
autologin-user-timeout=0
EOF
fi

# 6. Configure Chromium Fullscreen Kiosk Autostart on Desktop
USER_HOME=$(eval echo "~$REAL_USER")
AUTOSTART_DIR="$USER_HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat <<EOF > "$AUTOSTART_DIR/hfu-kiosk.desktop"
[Desktop Entry]
Type=Application
Name=HFU AI Workstation Kiosk
Exec=chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://localhost
X-GNOME-Autostart-enabled=true
EOF

chown -R "$REAL_USER:$REAL_USER" "$USER_HOME/.config"
echo "[SUCCESS] Kiosk Autostart configured for Desktop."

# 7. Create Systemd Autostart & Auto-Update Service
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

# 8. Make scripts executable
chmod +x scripts/*.sh

# 9. Run initial startup & container build
bash scripts/update.sh

echo "======================================================================"
echo "[COMPLETE] Setup finished! HFU AI Workstation is ready & active."
echo "Dashboard: http://localhost or http://192.168.4.1"
echo "======================================================================"
