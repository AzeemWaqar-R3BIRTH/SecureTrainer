#!/bin/bash
# Build script for Render.com deployment
# Installs system dependencies and Python packages

set -e  # Exit on error

echo "🔧 Installing system dependencies..."

# Install zbar library (required for pyzbar QR code scanning)
apt-get update
apt-get install -y libzbar0

echo "✅ System dependencies installed"

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build completed successfully"
