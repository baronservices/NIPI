#!/bin/bash
# Installation script for Network Intelligence Packet Inspector

set -e

echo "🚀 Installing Network Intelligence Packet Inspector..."

# Check if running as root for packet capture capabilities
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running as root - packet capture will be available"
else
    echo "⚠️  Not running as root - packet capture may be limited"
    echo "   Consider running with: sudo ./install.sh"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data backups

# Check Python version
echo "🐍 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not installed"
    exit 1
}

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo "❌ pip is required but not installed"
    exit 1
fi

# Initialize database
echo "🗄️ Initializing database..."
python3 scripts/init_database.py

# Set permissions
echo "🔒 Setting permissions..."
chmod +x src/main.py
chmod +x scripts/init_database.py

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Review configuration in config/config.yaml"
echo "   2. Start NIPI with: sudo python3 src/main.py"
echo "   3. Access web interface at: http://localhost:8080"
echo ""
echo "📚 For packet capture functionality, ensure:"
echo "   - Running with root privileges (sudo)"
echo "   - Network interface is accessible"
echo "   - No firewall blocking the web port"
echo ""
echo "🔗 Integration with existing NIP project:"
echo "   NIPI follows the same Baron Weather design patterns"
echo "   and can be linked from your existing NIP portal."