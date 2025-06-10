#!/usr/bin/env python3
"""
Basic NIPI launcher that works without additional dependencies.
Creates a simple web interface using only Python standard library.
"""

import http.server
import socketserver
import json
import sqlite3
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class NIPIHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for NIPI web interface."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/dashboard':
            self.serve_dashboard()
        elif parsed_path.path == '/api/stats':
            self.serve_api_stats()
        elif parsed_path.path == '/api/hosts':
            self.serve_api_hosts()
        elif parsed_path.path == '/api/packets':
            self.serve_api_packets()
        else:
            self.serve_static_content()
    
    def serve_dashboard(self):
        """Serve the main dashboard."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baron Weather - Network Intelligence Packet Inspector</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 20px; background-color: #f8f9fa; color: #333; line-height: 1.5;
        }
        
        .container {
            width: 100%; margin: 0; background: white; padding: 20px;
            border: 1px solid #dee2e6; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center; padding: 8px 40px;
            background: linear-gradient(135deg, #20c997 0%, #17a085 25%, #28a745 50%, #17a085 75%, #138d75 100%);
            border-radius: 20px; margin-bottom: 50px; color: white;
        }
        
        .logo-text { display: flex; flex-direction: column; line-height: 1; justify-content: center; align-items: center; }
        .logo-baron { font-size: 2.2rem; font-weight: 700; color: white; }
        .logo-weather { font-size: 1.4rem; font-weight: 500; color: rgba(255, 255, 255, 0.9); margin-top: -4px; }
        .subtitle { font-size: 18px; opacity: 0.9; margin: 10px 0 5px 0; }
        .version { font-size: 14px; opacity: 0.8; font-weight: 500; }
        
        .stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px; margin-bottom: 20px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6; border-radius: 8px; padding: 16px; text-align: center;
        }
        
        .stat-value {
            font-size: 1.8rem; font-weight: 700; color: #20c997; margin-bottom: 4px;
        }
        
        .stat-label { font-size: 0.9rem; color: #6c757d; font-weight: 500; }
        
        .card {
            background: white; border: 1px solid #dee2e6; border-radius: 8px;
            margin-bottom: 20px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .card-header {
            background: #343a40; color: white; padding: 12px 16px; font-weight: 600;
        }
        
        .card-body { padding: 16px; }
        
        .table {
            width: 100%; border-collapse: collapse; margin-top: 10px;
        }
        
        .table th, .table td {
            padding: 8px 12px; text-align: left; border-bottom: 1px solid #dee2e6;
        }
        
        .table th {
            background: #f8f9fa; font-weight: 600; color: #495057;
        }
        
        .table tr:hover { background: #f8f9fa; }
        
        .alert {
            padding: 12px 16px; border-radius: 4px; margin-bottom: 16px;
        }
        
        .alert-success {
            background: #d4edda; border: 1px solid #c3e6cb; color: #155724;
        }
        
        .btn {
            display: inline-block; padding: 8px 16px; background: #20c997;
            color: white; text-decoration: none; border-radius: 4px;
            font-weight: 500; border: none; cursor: pointer;
        }
        
        .status-indicator {
            display: inline-block; width: 8px; height: 8px;
            border-radius: 50%; margin-right: 8px;
        }
        
        .status-active { background: #28a745; }
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
            <div class="version">Basic Mode - Network Analysis System</div>
        </div>
        
        <div class="alert alert-success">
            <strong>🎉 NIPI Basic Mode Active!</strong> 
            NIPI is running successfully. This basic version demonstrates the interface design.
            <br><strong>Next:</strong> Install full dependencies for packet capture: <code>sudo apt install python3-pip python3-venv</code>
        </div>
        
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-value" id="packetCount">0</div>
                <div class="stat-label">Packets Captured</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="hostCount">0</div>
                <div class="stat-label">Network Hosts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">
                    <span class="status-indicator status-active"></span>Basic
                </div>
                <div class="stat-label">NIPI Status</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Ready</div>
                <div class="stat-label">System Status</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">📡 Network Hosts</div>
            <div class="card-body">
                <table class="table" id="hostsTable">
                    <thead>
                        <tr><th>IP Address</th><th>Hostname</th><th>Status</th><th>Last Seen</th></tr>
                    </thead>
                    <tbody id="hostsTableBody">
                        <tr><td colspan="4">Loading network hosts...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">📊 Recent Packet Activity</div>
            <div class="card-body">
                <table class="table" id="packetsTable">
                    <thead>
                        <tr><th>Time</th><th>Source</th><th>Destination</th><th>Protocol</th><th>Size</th></tr>
                    </thead>
                    <tbody id="packetsTableBody">
                        <tr><td colspan="5">Loading packet data...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">⚡ Quick Actions</div>
            <div class="card-body">
                <button onclick="refreshData()" class="btn">🔄 Refresh Data</button>
                <button onclick="showFullInstall()" class="btn">🚀 Full Install Guide</button>
            </div>
        </div>
    </div>
    
    <script>
        function loadData() {
            // Load hosts
            fetch('/api/hosts')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('hostsTableBody');
                    if (data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="4">No hosts data available yet. Install full NIPI for network scanning.</td></tr>';
                    } else {
                        tbody.innerHTML = data.map(host => 
                            `<tr><td>${host.ip_address}</td><td>${host.hostname || ''}</td><td>${host.status}</td><td>${host.last_seen || ''}</td></tr>`
                        ).join('');
                        document.getElementById('hostCount').textContent = data.length;
                    }
                })
                .catch(() => {
                    document.getElementById('hostsTableBody').innerHTML = '<tr><td colspan="4">Demo data - install full NIPI for live network scanning</td></tr>';
                });
                
            // Load packets
            fetch('/api/packets')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('packetsTableBody');
                    if (data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5">No packet data available yet. Install full NIPI for packet capture.</td></tr>';
                    } else {
                        tbody.innerHTML = data.map(packet => 
                            `<tr><td>${packet.timestamp}</td><td>${packet.src_ip}</td><td>${packet.dst_ip}</td><td>${packet.protocol}</td><td>${packet.packet_size} bytes</td></tr>`
                        ).join('');
                        document.getElementById('packetCount').textContent = data.length;
                    }
                })
                .catch(() => {
                    document.getElementById('packetsTableBody').innerHTML = '<tr><td colspan="5">Demo data - install full NIPI for live packet capture</td></tr>';
                });
        }
        
        function refreshData() { loadData(); }
        
        function showFullInstall() {
            alert('Full NIPI Installation:\\n\\n1. Install dependencies: sudo apt install python3-pip python3-venv\\n2. Run installer: sudo ./install-venv.sh\\n3. Start full NIPI: sudo python3 src/main.py\\n\\nThis will enable real-time packet capture and full network analysis!');
        }
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', loadData);
        
        // Auto-refresh every 30 seconds
        setInterval(loadData, 30000);
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_api_stats(self):
        """Serve API statistics."""
        stats = {"packets": 0, "hosts": 0, "status": "basic"}
        self.send_json_response(stats)
    
    def serve_api_hosts(self):
        """Serve hosts data from database."""
        try:
            if os.path.exists('data/nipi_demo.db'):
                conn = sqlite3.connect('data/nipi_demo.db')
                cursor = conn.cursor()
                cursor.execute("SELECT ip_address, hostname, status, last_seen FROM network_hosts")
                hosts = [{"ip_address": row[0], "hostname": row[1], "status": row[2], "last_seen": row[3]} 
                        for row in cursor.fetchall()]
                conn.close()
                self.send_json_response(hosts)
            else:
                self.send_json_response([])
        except Exception:
            self.send_json_response([])
    
    def serve_api_packets(self):
        """Serve packets data from database."""
        try:
            if os.path.exists('data/nipi_demo.db'):
                conn = sqlite3.connect('data/nipi_demo.db')
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp, src_ip, dst_ip, protocol, packet_size FROM packet_captures ORDER BY timestamp DESC LIMIT 10")
                packets = [{"timestamp": row[0], "src_ip": row[1], "dst_ip": row[2], "protocol": row[3], "packet_size": row[4]} 
                          for row in cursor.fetchall()]
                conn.close()
                self.send_json_response(packets)
            else:
                self.send_json_response([])
        except Exception:
            self.send_json_response([])
    
    def serve_static_content(self):
        """Serve static files."""
        if self.path == '/favicon.ico':
            self.send_response(404)
            self.end_headers()
            return
        super().do_GET()
    
    def send_json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def main():
    """Start NIPI basic server."""
    port = 8080
    
    print("🚀 Starting NIPI Basic Mode...")
    print(f"📱 Access NIPI at: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Ensure demo database exists
    if not os.path.exists('data/nipi_demo.db'):
        print("📊 Creating demo database...")
        os.system('python3 deploy-demo.py')
    
    try:
        with socketserver.TCPServer(("", port), NIPIHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 NIPI Basic Mode stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print("   Try: sudo lsof -ti:8080 | xargs sudo kill")
        else:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()