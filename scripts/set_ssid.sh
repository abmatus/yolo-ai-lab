#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Multi-Stand Access Point SSID Configuration Script
# Usage: sudo ./set_ssid.sh <STAND_NUMBER>
# Example: sudo ./set_ssid.sh 02 -> Sets SSID to AI-LAB-ORIN-02
# ==============================================================================

if [ "$#" -ne 1 ]; then
    echo "Usage: sudo $0 <STAND_NUMBER> (e.g., 01, 02, 03)"
    exit 1
fi

STAND_NO=$1
NEW_SSID="AI-LAB-ORIN-${STAND_NO}"
HOSTAPD_CONF="/etc/hostapd/hostapd.conf"
DNSMASQ_CONF="/etc/dnsmasq.conf"

echo "[HFU AI-LAB] Setting Access Point SSID to: ${NEW_SSID}..."

if [ -f "$HOSTAPD_CONF" ]; then
    sudo sed -i "s/^ssid=.*/ssid=${NEW_SSID}/g" "$HOSTAPD_CONF"
    echo "[OK] Updated ${HOSTAPD_CONF}"
else
    echo "[INFO] ${HOSTAPD_CONF} not found. Creating local config for Docker/hostapd..."
    mkdir -p config
    echo "ssid=${NEW_SSID}" > config/ap_ssid.txt
fi

# Restart hostapd service if running on host
if systemctl is-active --quiet hostapd; then
    sudo systemctl restart hostapd
    echo "[OK] Restarted hostapd service."
fi

echo "[SUCCESS] Stand SSID successfully configured to ${NEW_SSID}!"
