#!/bin/bash
# NIPI Dependencies Installation Script
# Run this script to install all required system dependencies for NIPI

set -e

echo "🔧 Installing NIPI System Dependencies..."

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root (use sudo)${NC}"
   echo "   Usage: sudo ./install-dependencies.sh"
   exit 1
fi

echo -e "${YELLOW}📦 Updating package lists...${NC}"
apt update

echo -e "${YELLOW}🐍 Installing Python development environment...${NC}"
apt install -y python3 python3-pip python3-venv python3-full python3-dev

echo -e "${YELLOW}📡 Installing packet capture dependencies...${NC}"
apt install -y libpcap-dev tcpdump

echo -e "${YELLOW}🔒 Installing cryptography dependencies...${NC}"
apt install -y build-essential libssl-dev libffi-dev

echo -e "${YELLOW}📊 Installing system monitoring tools...${NC}"
apt install -y net-tools ifstat iftop htop

echo -e "${YELLOW}🌐 Installing network utilities...${NC}"
apt install -y nmap traceroute whois dnsutils

echo -e "${YELLOW}📝 Installing development tools (optional)...${NC}"
apt install -y git curl wget vim nano

echo -e "${YELLOW}🗃️ Installing database tools (optional)...${NC}"
apt install -y sqlite3 postgresql-client

echo ""
echo -e "${GREEN}✅ All NIPI dependencies installed successfully!${NC}"
echo ""
echo "📋 Next steps:"
echo "   1. Run NIPI installer: ./install-venv.sh"
echo "   2. Start NIPI: sudo ./start-nipi.sh"
echo ""
echo "📚 Installed packages:"
echo "   • Python 3 development environment"
echo "   • Packet capture libraries (libpcap)"
echo "   • Network monitoring tools"
echo "   • Cryptography dependencies"
echo "   • Development and database tools"
echo ""
echo "🔗 Ready for NIPI installation!"