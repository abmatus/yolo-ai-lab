#!/usr/bin/env bash
# ==============================================================================
# HFU AI-LAB: Session Reset Script
# Clears student datasets, annotations, trained models and generated reports
# ==============================================================================

WORKSPACE_DIR="${WORKSPACE_DIR:-/workspace/student_data}"

echo "[HFU AI-LAB] Resetting student lab workspace..."

if [ -d "$WORKSPACE_DIR" ]; then
    rm -rf "${WORKSPACE_DIR:?}"/*
fi

mkdir -p "$WORKSPACE_DIR/dataset/images/train"
mkdir -p "$WORKSPACE_DIR/dataset/images/val"
mkdir -p "$WORKSPACE_DIR/dataset/labels/train"
mkdir -p "$WORKSPACE_DIR/dataset/labels/val"
mkdir -p "$WORKSPACE_DIR/runs"
mkdir -p "$WORKSPACE_DIR/reports"

echo "[SUCCESS] Workspace reset complete. Station is ready for the next student team."
