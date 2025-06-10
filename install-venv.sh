#!/bin/bash
# Installation script for NIPI using virtual environment

set -e

echo "🚀 Installing Network Intelligence Packet Inspector (NIPI)..."

# Check if running as root for packet capture capabilities
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running as root - packet capture will be available"
else
    echo "⚠️  Not running as root - packet capture may be limited"
    echo "   Consider running with: sudo ./install-venv.sh"
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

# Create virtual environment
echo "🌐 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies in virtual environment..."
source venv/bin/activate
pip install --upgrade pip

# Try to install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install minimal dependencies manually
    echo "Installing minimal dependencies..."
    pip install flask sqlalchemy
    echo "⚠️  Note: For full packet capture, install: pip install scapy psutil"
fi

# Initialize database
echo "🗄️ Initializing database..."
python scripts/init_database.py

# Set permissions
echo "🔒 Setting permissions..."
chmod +x src/main.py
chmod +x scripts/init_database.py

# Create start script
echo "📝 Creating start script..."
cat > start-nipi.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🚀 Starting NIPI..."
echo "📱 Access at: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop"
python src/main.py "$@"
EOF
chmod +x start-nipi.sh

echo ""
echo "✅ NIPI installation completed successfully!"
echo ""
echo "📋 To start NIPI:"
echo "   ./start-nipi.sh"
echo ""
echo "📋 To start with root (for packet capture):"
echo "   sudo ./start-nipi.sh"
echo ""
echo "🌐 Access web interface at: http://localhost:8080"
echo ""
echo "📚 Virtual environment created in: ./venv/"
echo "🔗 Integration ready with existing Baron Weather NIP project"