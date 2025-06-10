"""Flask web application for Network Intelligence Packet Inspector."""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import func, desc
import yaml

from ..database.connection import init_database, get_db_session
from ..database.models import (
    PacketCapture, FlowSession, NetworkHost, BandwidthStats,
    SecurityEvent, PerformanceMetrics, SystemConfig
)
from ..capture.packet_engine import PacketCaptureEngine


class NIPIWebApp:
    """Network Intelligence Packet Inspector Web Application."""
    
    def __init__(self, config_path: str = None):
        """Initialize the web application."""
        self.app = Flask(__name__, 
                        template_folder='../../templates',
                        static_folder='../../static')
        self.app.secret_key = 'nipi-secret-key-change-in-production'
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize database
        init_database(config_path)
        
        # Initialize packet capture engine
        self.capture_engine = PacketCaptureEngine(self.config['capture'])
        
        # Register routes
        self._register_routes()
    
    def _load_config(self, config_path: str = None) -> dict:
        """Load application configuration."""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'config.yaml'
            )
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _register_routes(self):
        """Register all Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard view."""
            try:
                with get_db_session() as session:
                    # Get capture statistics
                    capture_stats = self.capture_engine.get_statistics()
                    
                    # Get recent packet count
                    hour_ago = datetime.utcnow() - timedelta(hours=1)
                    recent_packets = session.query(PacketCapture).filter(
                        PacketCapture.timestamp >= hour_ago
                    ).count()
                    
                    # Get active hosts count
                    day_ago = datetime.utcnow() - timedelta(days=1)
                    active_hosts = session.query(NetworkHost).filter(
                        NetworkHost.last_seen >= day_ago
                    ).count()
                    
                    # Get security events count
                    security_events = session.query(SecurityEvent).filter(
                        SecurityEvent.timestamp >= day_ago
                    ).count()
                    
                    # Get top talkers
                    top_talkers = session.query(
                        BandwidthStats.host_id,
                        NetworkHost.ip_address,
                        NetworkHost.hostname,
                        func.sum(BandwidthStats.bytes_sent + BandwidthStats.bytes_received).label('total_bytes')
                    ).join(NetworkHost).filter(
                        BandwidthStats.timestamp >= day_ago
                    ).group_by(BandwidthStats.host_id).order_by(
                        desc('total_bytes')
                    ).limit(10).all()
                    
                    # Get recent security events
                    recent_security_events = session.query(SecurityEvent).filter(
                        SecurityEvent.timestamp >= day_ago
                    ).order_by(desc(SecurityEvent.timestamp)).limit(10).all()
                    
                    return render_template('dashboard.html',
                                         capture_stats=capture_stats,
                                         recent_packets=recent_packets,
                                         active_hosts=active_hosts,
                                         security_events=security_events,
                                         top_talkers=top_talkers,
                                         recent_security_events=recent_security_events)
            except Exception as e:
                return render_template('error.html', error=str(e))
        
        @self.app.route('/capture')
        def capture():
            """Packet capture control view."""
            interfaces = self.capture_engine.get_available_interfaces()
            stats = self.capture_engine.get_statistics()
            is_running = self.capture_engine.is_running
            
            return render_template('capture.html',
                                 interfaces=interfaces,
                                 stats=stats,
                                 is_running=is_running)
        
        @self.app.route('/capture/start', methods=['POST'])
        def start_capture():
            """Start packet capture."""
            try:
                interface = request.form.get('interface', 'auto')
                packet_filter = request.form.get('filter', '')
                
                self.capture_engine.start_capture(interface, packet_filter)
                return jsonify({'status': 'success', 'message': 'Packet capture started'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/capture/stop', methods=['POST'])
        def stop_capture():
            """Stop packet capture."""
            try:
                self.capture_engine.stop_capture()
                return jsonify({'status': 'success', 'message': 'Packet capture stopped'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/capture/stats')
        def capture_stats():
            """Get capture statistics API."""
            stats = self.capture_engine.get_statistics()
            return jsonify(stats)
        
        @self.app.route('/analysis')
        def analysis():
            """Network analysis view."""
            try:
                with get_db_session() as session:
                    # Get protocol distribution
                    protocol_stats = session.query(
                        PacketCapture.protocol,
                        func.count(PacketCapture.id).label('count')
                    ).group_by(PacketCapture.protocol).all()
                    
                    # Get bandwidth over time (last 24 hours)
                    day_ago = datetime.utcnow() - timedelta(days=1)
                    bandwidth_data = session.query(
                        func.date_trunc('hour', BandwidthStats.timestamp).label('hour'),
                        func.sum(BandwidthStats.bytes_sent + BandwidthStats.bytes_received).label('total_bytes')
                    ).filter(
                        BandwidthStats.timestamp >= day_ago
                    ).group_by('hour').order_by('hour').all()
                    
                    return render_template('analysis.html',
                                         protocol_stats=protocol_stats,
                                         bandwidth_data=bandwidth_data)
            except Exception as e:
                return render_template('error.html', error=str(e))
        
        @self.app.route('/security')
        def security():
            """Security monitoring view."""
            try:
                with get_db_session() as session:
                    # Get security events
                    events = session.query(SecurityEvent).order_by(
                        desc(SecurityEvent.timestamp)
                    ).limit(100).all()
                    
                    # Get threat statistics
                    threat_stats = session.query(
                        SecurityEvent.event_type,
                        SecurityEvent.severity,
                        func.count(SecurityEvent.id).label('count')
                    ).group_by(SecurityEvent.event_type, SecurityEvent.severity).all()
                    
                    return render_template('security.html',
                                         events=events,
                                         threat_stats=threat_stats)
            except Exception as e:
                return render_template('error.html', error=str(e))
        
        @self.app.route('/performance')
        def performance():
            """Performance monitoring view."""
            try:
                with get_db_session() as session:
                    # Get performance metrics
                    day_ago = datetime.utcnow() - timedelta(days=1)
                    metrics = session.query(PerformanceMetrics).filter(
                        PerformanceMetrics.timestamp >= day_ago
                    ).order_by(desc(PerformanceMetrics.timestamp)).limit(100).all()
                    
                    return render_template('performance.html', metrics=metrics)
            except Exception as e:
                return render_template('error.html', error=str(e))
        
        @self.app.route('/settings')
        def settings():
            """Application settings view."""
            return render_template('settings.html', config=self.config)
        
        @self.app.route('/api/packets/recent')
        def api_recent_packets():
            """API endpoint for recent packets."""
            try:
                limit = request.args.get('limit', 100, type=int)
                with get_db_session() as session:
                    packets = session.query(PacketCapture).order_by(
                        desc(PacketCapture.timestamp)
                    ).limit(limit).all()
                    
                    packet_data = []
                    for packet in packets:
                        packet_data.append({
                            'timestamp': packet.timestamp.isoformat(),
                            'src_ip': packet.src_ip,
                            'dst_ip': packet.dst_ip,
                            'src_port': packet.src_port,
                            'dst_port': packet.dst_port,
                            'protocol': packet.protocol,
                            'packet_size': packet.packet_size
                        })
                    
                    return jsonify(packet_data)
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/hosts')
        def api_hosts():
            """API endpoint for network hosts."""
            try:
                with get_db_session() as session:
                    hosts = session.query(NetworkHost).all()
                    
                    host_data = []
                    for host in hosts:
                        host_data.append({
                            'ip_address': host.ip_address,
                            'hostname': host.hostname,
                            'mac_address': host.mac_address,
                            'vendor': host.vendor,
                            'os_family': host.os_family,
                            'last_seen': host.last_seen.isoformat() if host.last_seen else None,
                            'is_active': host.is_active
                        })
                    
                    return jsonify(host_data)
            except Exception as e:
                return jsonify({'error': str(e)})
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Run the Flask application."""
        if host is None:
            host = self.config['app'].get('host', '0.0.0.0')
        if port is None:
            port = self.config['app'].get('port', 8080)
        if debug is None:
            debug = self.config['app'].get('debug', False)
        
        self.app.run(host=host, port=port, debug=debug)


def create_app(config_path: str = None) -> Flask:
    """Create Flask application instance."""
    web_app = NIPIWebApp(config_path)
    return web_app.app