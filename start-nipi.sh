#!/bin/bash
# NIPI Start Script

cd "$(dirname "$0")"

echo "🚀 Starting Network Intelligence Packet Inspector..."
echo "📱 Access NIPI at: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Activate virtual environment and start NIPI
source venv/bin/activate
export PYTHONPATH=/home/tony/network-intelligence-packet-inspector
python src/main.py "$@"