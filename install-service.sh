#!/bin/bash

# NIPI Service Installation Script
# This script installs NIPI as a systemd service to start automatically at boot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="nipi"
SERVICE_FILE="${SCRIPT_DIR}/${SERVICE_NAME}.service"

echo "🔧 Installing NIPI as a system service..."
echo "========================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo"
    echo "Usage: sudo ./install-service.sh"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "${SCRIPT_DIR}/venv" ]; then
    echo "❌ Virtual environment not found. Please run install-venv.sh first."
    exit 1
fi

# Stop any existing service
echo "🛑 Stopping existing NIPI service (if running)..."
systemctl stop $SERVICE_NAME 2>/dev/null || true
systemctl disable $SERVICE_NAME 2>/dev/null || true

# Copy service file to systemd directory
echo "📋 Installing service file..."
cp "$SERVICE_FILE" "/etc/systemd/system/"

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable and start the service
echo "✅ Enabling NIPI service..."
systemctl enable $SERVICE_NAME

echo "▶️  Starting NIPI service..."
systemctl start $SERVICE_NAME

# Check service status
echo ""
echo "📊 Service Status:"
systemctl status $SERVICE_NAME --no-pager

echo ""
echo "✅ NIPI service installation complete!"
echo ""
echo "🔧 Service Management Commands:"
echo "   Start:   sudo systemctl start $SERVICE_NAME"
echo "   Stop:    sudo systemctl stop $SERVICE_NAME"
echo "   Restart: sudo systemctl restart $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🌐 NIPI will now start automatically at boot"
echo "   Access: http://localhost:8080"