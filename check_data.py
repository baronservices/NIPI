#!/usr/bin/env python3
"""Check if packet data exists in database."""

import sys
sys.path.insert(0, '/home/tony/network-intelligence-packet-inspector')

from src.database.connection import get_db_session, init_database
from src.database.models import PacketCapture, BandwidthStats
from sqlalchemy import func
from datetime import datetime, timedelta

def check_packet_data():
    """Check if packet capture data exists."""
    try:
        with get_db_session() as session:
            # Count total packets
            total_packets = session.query(PacketCapture).count()
            print(f"📦 Total packets in database: {total_packets}")
            
            # Count recent packets (last hour)
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent_packets = session.query(PacketCapture).filter(
                PacketCapture.timestamp >= hour_ago
            ).count()
            print(f"🕐 Recent packets (last hour): {recent_packets}")
            
            # Get protocol distribution
            protocols = session.query(
                PacketCapture.protocol,
                func.count(PacketCapture.id).label('count')
            ).group_by(PacketCapture.protocol).all()
            
            print(f"🔌 Protocol distribution:")
            for protocol, count in protocols:
                print(f"   {protocol}: {count} packets")
            
            # Show sample packets
            sample_packets = session.query(PacketCapture).limit(5).all()
            print(f"📋 Sample packets:")
            for packet in sample_packets:
                print(f"   {packet.timestamp} | {packet.src_ip} → {packet.dst_ip} | {packet.protocol}")
            
            # Check bandwidth stats
            bandwidth_count = session.query(BandwidthStats).count()
            print(f"📈 Bandwidth statistics records: {bandwidth_count}")
            
    except Exception as e:
        print(f"❌ Error checking data: {e}")

if __name__ == "__main__":
    print("🔍 Checking NIPI Database Contents")
    print("=" * 40)
    
    # Initialize database first
    try:
        init_database()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database init: {e}")
    
    check_packet_data()