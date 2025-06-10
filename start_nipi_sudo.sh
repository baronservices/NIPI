#!/bin/bash

# NIPI Startup Script with Root Privileges
# This script handles starting NIPI with the necessary root privileges for packet capture

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting NIPI with Root Privileges..."
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install-venv.sh first."
    exit 1
fi

# Fix database permissions
echo "🔧 Fixing database permissions..."
sudo chown -R $USER:$USER database/
sudo chmod 664 database/*.db 2>/dev/null || true

# Stop any existing NIPI processes
echo "🛑 Stopping existing NIPI processes..."
sudo pkill -f "python.*main.py" 2>/dev/null || true
sleep 2

# Start NIPI with root privileges
echo "▶️  Starting NIPI server..."
echo "🌐 Access: http://localhost:8080"
echo "🔴 Press Ctrl+C to stop"
echo ""

# Use the virtual environment Python with sudo
sudo PYTHONPATH="$SCRIPT_DIR" "$SCRIPT_DIR/venv/bin/python" src/main.py --host 0.0.0.0 --port 8080