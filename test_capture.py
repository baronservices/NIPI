#!/usr/bin/env python3
"""Quick test to check packet capture capabilities."""

import os
import sys
from scapy.all import get_if_list, sniff
import psutil

def test_permissions():
    """Test if we have root privileges."""
    print(f"Current user ID: {os.geteuid()}")
    if os.geteuid() != 0:
        print("❌ Running without root privileges")
        print("💡 Packet capture requires root access")
        return False
    else:
        print("✅ Running with root privileges")
        return True

def test_interfaces():
    """Test network interface detection."""
    try:
        interfaces = get_if_list()
        print(f"📡 Available interfaces: {interfaces}")
        
        active_interfaces = []
        for interface in interfaces:
            try:
                stats = psutil.net_if_stats().get(interface)
                if stats and stats.isup:
                    active_interfaces.append(interface)
                    print(f"✅ {interface}: UP")
                else:
                    print(f"❌ {interface}: DOWN")
            except Exception as e:
                print(f"⚠️  {interface}: Error - {e}")
        
        return active_interfaces
    except Exception as e:
        print(f"❌ Error getting interfaces: {e}")
        return []

def test_packet_capture():
    """Test basic packet capture."""
    try:
        print("🔍 Testing packet capture for 3 seconds...")
        packets = sniff(timeout=3, count=5)
        print(f"✅ Captured {len(packets)} packets successfully")
        return True
    except Exception as e:
        print(f"❌ Packet capture failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 NIPI Packet Capture Test")
    print("=" * 40)
    
    has_root = test_permissions()
    print()
    
    interfaces = test_interfaces()
    print()
    
    if has_root and interfaces:
        test_packet_capture()
    else:
        print("💡 To enable packet capture:")
        print("   sudo python3 test_capture.py")
        print("   sudo python3 src/main.py --host 0.0.0.0 --port 8080")