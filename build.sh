#!/usr/bin/env bash
# Build script for Render.com deployment
# Installs system dependencies and Python packages

set -o errexit  # Exit on error

echo "🔧 Installing system dependencies..."

# Install zbar library (required for pyzbar QR code scanning)
# On Render, apt-get commands run with appropriate permissions
apt-get update -qq
apt-get install -y -qq libzbar0 libzbar-dev

echo "✅ System dependencies installed"

echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Build completed successfully"
