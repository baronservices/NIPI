#!/usr/bin/env python3
"""
Demo deployment script for NIPI that works without root privileges.
This creates a mock version for demonstration purposes.
"""

import os
import sys
import sqlite3
from pathlib import Path

def create_demo_database():
    """Create a demo database with sample data."""
    db_path = "data/nipi_demo.db"
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create simplified tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packet_captures (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            src_ip TEXT,
            dst_ip TEXT,
            protocol TEXT,
            packet_size INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS network_hosts (
            id INTEGER PRIMARY KEY,
            ip_address TEXT UNIQUE,
            hostname TEXT,
            status TEXT,
            last_seen TEXT
        )
    """)
    
    # Insert sample data
    sample_packets = [
        ('2025-06-10 00:01:00', '192.168.10.1', '192.168.10.2', 'TCP', 1500),
        ('2025-06-10 00:01:01', '192.168.10.2', '192.168.10.1', 'TCP', 64),
        ('2025-06-10 00:01:02', '192.168.10.3', '8.8.8.8', 'UDP', 128),
        ('2025-06-10 00:01:03', '192.168.10.1', '74.51.117.5', 'HTTP', 2048),
        ('2025-06-10 00:01:04', '192.168.10.4', '192.168.10.1', 'SSH', 256),
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO packet_captures (timestamp, src_ip, dst_ip, protocol, packet_size) VALUES (?, ?, ?, ?, ?)",
        sample_packets
    )
    
    sample_hosts = [
        ('192.168.10.1', 'gateway.baron.hsv', 'UP', '2025-06-10 00:01:00'),
        ('192.168.10.2', 'gpu-node-1.baron.hsv', 'UP', '2025-06-10 00:01:00'),
        ('192.168.10.3', 'apollo-nas.baron.hsv', 'UP', '2025-06-10 00:01:00'),
        ('192.168.10.4', 'workstation.baron.hsv', 'UP', '2025-06-10 00:01:00'),
        ('74.51.117.5', 'external-server.com', 'UP', '2025-06-10 00:01:00'),
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO network_hosts (ip_address, hostname, status, last_seen) VALUES (?, ?, ?, ?)",
        sample_hosts
    )
    
    conn.commit()
    conn.close()
    print(f"✅ Demo database created: {db_path}")

def create_demo_web_server():
    """Create a simple demo web server using only standard library."""
    content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baron Weather - Network Intelligence Packet Inspector (Demo)</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.5;
        }
        
        .container {
            width: 100%;
            margin: 0;
            background: white;
            padding: 20px;
            border: 1px solid #dee2e6;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            padding: 8px 40px;
            background: linear-gradient(135deg, #20c997 0%, #17a085 25%, #28a745 50%, #17a085 75%, #138d75 100%);
            border-radius: 20px;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
            max-width: 1600px;
            margin-left: auto;
            margin-right: auto;
            color: white;
        }
        
        .logo-text {
            display: flex;
            flex-direction: column;
            line-height: 1;
            justify-content: center;
            align-items: center;
        }
        
        .logo-baron {
            font-size: 2.2rem;
            font-weight: 700;
            color: white;
        }
        
        .logo-weather {
            font-size: 1.4rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
            margin-top: -4px;
        }
        
        .subtitle {
            font-size: 18px;
            opacity: 0.9;
            margin: 10px 0 5px 0;
        }
        
        .version {
            font-size: 14px;
            opacity: 0.8;
            font-weight: 500;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #20c997;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #6c757d;
            font-weight: 500;
        }
        
        .alert {
            padding: 12px 16px;
            border-radius: 4px;
            margin-bottom: 16px;
        }
        
        .alert-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        
        .alert-warning {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        
        .card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .card-header {
            background: #343a40;
            color: white;
            padding: 12px 16px;
            font-weight: 600;
        }
        
        .card-body {
            padding: 16px;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .table th,
        .table td {
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        .table tr:hover {
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-text">
                <div class="logo-baron">BARON</div>
                <div class="logo-weather">WEATHER</div>
            </div>
            <div class="subtitle">Network Intelligence Packet Inspector</div>
            <div class="version">Demo Mode - Real-time Network Analysis & Security Monitoring</div>
        </div>
        
        <div class="alert alert-warning">
            <strong>Demo Mode:</strong> This is a demonstration version of NIPI. 
            For full packet capture functionality, install with root privileges: <code>sudo ./install.sh</code>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">5</div>
                <div class="stat-label">Sample Packets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">5</div>
                <div class="stat-label">Network Hosts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div class="stat-label">Protocols</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Demo</div>
                <div class="stat-label">Capture Status</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">📡 Sample Network Hosts</div>
            <div class="card-body">
                <table class="table">
                    <thead>
                        <tr>
                            <th>IP Address</th>
                            <th>Hostname</th>
                            <th>Status</th>
                            <th>Last Seen</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>192.168.10.1</td><td>gateway.baron.hsv</td><td>UP</td><td>2025-06-10 00:01</td></tr>
                        <tr><td>192.168.10.2</td><td>gpu-node-1.baron.hsv</td><td>UP</td><td>2025-06-10 00:01</td></tr>
                        <tr><td>192.168.10.3</td><td>apollo-nas.baron.hsv</td><td>UP</td><td>2025-06-10 00:01</td></tr>
                        <tr><td>192.168.10.4</td><td>workstation.baron.hsv</td><td>UP</td><td>2025-06-10 00:01</td></tr>
                        <tr><td>74.51.117.5</td><td>external-server.com</td><td>UP</td><td>2025-06-10 00:01</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">📊 Sample Packet Captures</div>
            <div class="card-body">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Source</th>
                            <th>Destination</th>
                            <th>Protocol</th>
                            <th>Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>00:01:00</td><td>192.168.10.1</td><td>192.168.10.2</td><td>TCP</td><td>1500 bytes</td></tr>
                        <tr><td>00:01:01</td><td>192.168.10.2</td><td>192.168.10.1</td><td>TCP</td><td>64 bytes</td></tr>
                        <tr><td>00:01:02</td><td>192.168.10.3</td><td>8.8.8.8</td><td>UDP</td><td>128 bytes</td></tr>
                        <tr><td>00:01:03</td><td>192.168.10.1</td><td>74.51.117.5</td><td>HTTP</td><td>2048 bytes</td></tr>
                        <tr><td>00:01:04</td><td>192.168.10.4</td><td>192.168.10.1</td><td>SSH</td><td>256 bytes</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="alert alert-info">
            <strong>Next Steps:</strong><br>
            1. Install dependencies: <code>sudo apt update && sudo apt install python3-pip</code><br>
            2. Install NIPI: <code>sudo ./install.sh</code><br>
            3. Start full application: <code>sudo python3 src/main.py</code>
        </div>
    </div>
</body>
</html>
"""
    
    with open("nipi_demo.html", "w") as f:
        f.write(content)
    
    print("✅ Demo web page created: nipi_demo.html")

def main():
    """Main demo deployment function."""
    print("🚀 Deploying NIPI Demo Mode...")
    
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    print("✅ Directories created")
    
    # Create demo database
    create_demo_database()
    
    # Create demo web page
    create_demo_web_server()
    
    print()
    print("✅ NIPI Demo deployed successfully!")
    print()
    print("📋 Demo Access:")
    print("   - Open: nipi_demo.html in your browser")
    print("   - View sample data and interface design")
    print()
    print("🔧 For full functionality:")
    print("   1. Install pip: sudo apt update && sudo apt install python3-pip")
    print("   2. Run: sudo ./install.sh")
    print("   3. Start: sudo python3 src/main.py")

if __name__ == '__main__':
    main()