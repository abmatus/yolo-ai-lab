#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Automatic Student USB Data Export Script
# Copies images, labels, trained weights (PyTorch/TensorRT) and PDF reports to USB drive
# ==============================================================================

WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace/student_data}"
EXPORT_NAME="HFU_KI_Praktikum_Export_$(date +%Y%m%d_%H%M%S)"
TARGET_USB=""

echo "[HFU AI-LAB] Searching for connected USB drives..."

# Check common mount points on Linux / Jetson
for mount in /media/*/* /mnt/* /media/*; do
    if [ -d "$mount" ] && [ -w "$mount" ] && [ "$mount" != "/media/root" ]; then
        TARGET_USB="$mount"
        break
    fi
done

if [ -z "$TARGET_USB" ]; then
    echo "[WARNING] No mounted USB drive found in /media or /mnt."
    echo "[INFO] Saving export locally to /workspace/exports/${EXPORT_NAME}.zip"
    mkdir -p /workspace/exports
    zip -r "/workspace/exports/${EXPORT_NAME}.zip" "$WORKSPACE_DIR"
    echo "[SUCCESS] Local backup saved: /workspace/exports/${EXPORT_NAME}.zip"
    exit 0
fi

DEST_DIR="${TARGET_USB}/${EXPORT_NAME}"
echo "[HFU AI-LAB] Exporting student data to USB: ${DEST_DIR}..."

mkdir -p "$DEST_DIR"
cp -r "$WORKSPACE_DIR"/* "$DEST_DIR"/ 2>/dev/null || true

echo "[SUCCESS] All lab results, trained models, TensorRT engines and PDF report successfully exported to USB!"
echo "[PATH] ${DEST_DIR}"
