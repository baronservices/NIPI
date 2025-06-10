"""Packet capture engine using Scapy."""

import time
import threading
import logging
from datetime import datetime
from typing import Callable, Optional, Dict, Any
from queue import Queue
import psutil
import hashlib

from scapy.all import sniff, get_if_list, Ether, IP, IPv6, TCP, UDP, ICMP
from scapy.packet import Packet

from src.database.models import PacketCapture, FlowSession
from src.database.connection import get_db_session


logger = logging.getLogger(__name__)


class PacketCaptureEngine:
    """Real-time packet capture and processing engine."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the packet capture engine."""
        self.config = config
        self.is_running = False
        self.capture_thread = None
        self.packet_queue = Queue(maxsize=10000)
        self.processor_thread = None
        
        # Statistics
        self.stats = {
            'packets_captured': 0,
            'packets_processed': 0,
            'packets_dropped': 0,
            'bytes_captured': 0,
            'start_time': None
        }
        
        # Flow tracking
        self.active_flows = {}
        self.flow_timeout = 300  # 5 minutes
        
    def get_available_interfaces(self) -> list:
        """Get list of available network interfaces."""
        try:
            interfaces = get_if_list()
            return interfaces
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []
    
    def auto_select_interface(self) -> str:
        """Automatically select the best network interface."""
        interfaces = self.get_available_interfaces()
        
        # Try to find active interfaces with traffic
        for interface in interfaces:
            if interface in ['lo', 'localhost']:
                continue
            
            # Check if interface has IP and is up
            try:
                stats = psutil.net_if_stats().get(interface)
                if stats and stats.isup:
                    return interface
            except Exception:
                continue
        
        # Fallback to first non-loopback interface
        for interface in interfaces:
            if interface not in ['lo', 'localhost']:
                return interface
        
        return interfaces[0] if interfaces else 'eth0'
    
    def start_capture(self, interface: str = None, packet_filter: str = None):
        """Start packet capture on specified interface."""
        if self.is_running:
            logger.warning("Packet capture is already running")
            return
        
        if interface is None or interface == 'auto':
            interface = self.auto_select_interface()
        
        logger.info(f"Starting packet capture on interface: {interface}")
        
        self.is_running = True
        self.stats['start_time'] = datetime.utcnow()
        
        # Start packet processor thread
        self.processor_thread = threading.Thread(
            target=self._process_packets, daemon=True
        )
        self.processor_thread.start()
        
        # Start packet capture thread
        self.capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(interface, packet_filter),
            daemon=True
        )
        self.capture_thread.start()
        
        logger.info("Packet capture started successfully")
    
    def stop_capture(self):
        """Stop packet capture."""
        if not self.is_running:
            logger.warning("Packet capture is not running")
            return
        
        logger.info("Stopping packet capture...")
        self.is_running = False
        
        # Wait for threads to finish
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        if self.processor_thread:
            self.processor_thread.join(timeout=5)
        
        logger.info("Packet capture stopped")
    
    def _capture_packets(self, interface: str, packet_filter: str = None):
        """Internal method to capture packets."""
        try:
            def packet_handler(packet):
                if not self.is_running:
                    return
                
                try:
                    # Add packet to processing queue
                    if not self.packet_queue.full():
                        self.packet_queue.put(packet)
                        self.stats['packets_captured'] += 1
                        self.stats['bytes_captured'] += len(packet)
                    else:
                        self.stats['packets_dropped'] += 1
                        
                except Exception as e:
                    logger.error(f"Error handling packet: {e}")
            
            # Start sniffing
            sniff(
                iface=interface,
                prn=packet_handler,
                filter=packet_filter,
                store=False,
                stop_filter=lambda x: not self.is_running
            )
            
        except Exception as e:
            logger.error(f"Error in packet capture: {e}")
            self.is_running = False
    
    def _process_packets(self):
        """Process captured packets and store in database."""
        while self.is_running or not self.packet_queue.empty():
            try:
                # Get packet from queue with timeout
                if not self.packet_queue.empty():
                    packet = self.packet_queue.get(timeout=1)
                    self._analyze_packet(packet)
                    self.stats['packets_processed'] += 1
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error processing packet: {e}")
    
    def _analyze_packet(self, packet: Packet):
        """Analyze and store packet information."""
        try:
            # Extract packet information
            packet_info = self._extract_packet_info(packet)
            
            if packet_info:
                # Store packet in database
                self._store_packet(packet_info)
                
                # Update flow session
                self._update_flow_session(packet_info)
                
        except Exception as e:
            logger.error(f"Error analyzing packet: {e}")
    
    def _extract_packet_info(self, packet: Packet) -> Optional[Dict[str, Any]]:
        """Extract relevant information from packet."""
        try:
            info = {
                'timestamp': datetime.utcnow(),
                'packet_size': len(packet),
                'interface': getattr(packet, 'sniffed_on', 'unknown')
            }
            
            # Handle Ethernet layer
            if Ether in packet:
                info['src_mac'] = packet[Ether].src
                info['dst_mac'] = packet[Ether].dst
            
            # Handle IP layer (IPv4/IPv6)
            if IP in packet:
                ip_layer = packet[IP]
                info.update({
                    'src_ip': ip_layer.src,
                    'dst_ip': ip_layer.dst,
                    'protocol': ip_layer.proto,
                    'ttl': ip_layer.ttl,
                    'payload_size': len(ip_layer.payload) if ip_layer.payload else 0
                })
            elif IPv6 in packet:
                ip_layer = packet[IPv6]
                info.update({
                    'src_ip': ip_layer.src,
                    'dst_ip': ip_layer.dst,
                    'protocol': ip_layer.nh,
                    'ttl': ip_layer.hlim,
                    'payload_size': len(ip_layer.payload) if ip_layer.payload else 0
                })
            else:
                # Non-IP packet, skip for now
                return None
            
            # Handle transport layer
            if TCP in packet:
                tcp_layer = packet[TCP]
                info.update({
                    'src_port': tcp_layer.sport,
                    'dst_port': tcp_layer.dport,
                    'protocol_name': 'TCP',
                    'flags': str(tcp_layer.flags)
                })
            elif UDP in packet:
                udp_layer = packet[UDP]
                info.update({
                    'src_port': udp_layer.sport,
                    'dst_port': udp_layer.dport,
                    'protocol_name': 'UDP',
                    'flags': ''
                })
            elif ICMP in packet:
                info.update({
                    'src_port': None,
                    'dst_port': None,
                    'protocol_name': 'ICMP',
                    'flags': ''
                })
            else:
                info.update({
                    'src_port': None,
                    'dst_port': None,
                    'protocol_name': 'OTHER',
                    'flags': ''
                })
            
            return info
            
        except Exception as e:
            logger.error(f"Error extracting packet info: {e}")
            return None
    
    def _store_packet(self, packet_info: Dict[str, Any]):
        """Store packet information in database."""
        try:
            with get_db_session() as session:
                packet_record = PacketCapture(
                    timestamp=packet_info['timestamp'],
                    src_ip=packet_info.get('src_ip'),
                    dst_ip=packet_info.get('dst_ip'),
                    src_port=packet_info.get('src_port'),
                    dst_port=packet_info.get('dst_port'),
                    protocol=packet_info.get('protocol_name'),
                    packet_size=packet_info['packet_size'],
                    ttl=packet_info.get('ttl'),
                    flags=packet_info.get('flags'),
                    payload_size=packet_info.get('payload_size'),
                    interface=packet_info['interface']
                )
                session.add(packet_record)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error storing packet: {e}")
    
    def _update_flow_session(self, packet_info: Dict[str, Any]):
        """Update or create flow session for packet."""
        try:
            # Create flow identifier
            flow_id = self._create_flow_id(packet_info)
            
            current_time = datetime.utcnow()
            
            # Check if flow exists in memory
            if flow_id in self.active_flows:
                flow = self.active_flows[flow_id]
                flow['last_seen'] = current_time
                flow['packet_count'] += 1
                flow['bytes_transferred'] += packet_info['packet_size']
            else:
                # Create new flow
                self.active_flows[flow_id] = {
                    'session_id': flow_id,
                    'src_ip': packet_info.get('src_ip'),
                    'dst_ip': packet_info.get('dst_ip'),
                    'src_port': packet_info.get('src_port'),
                    'dst_port': packet_info.get('dst_port'),
                    'protocol': packet_info.get('protocol_name'),
                    'start_time': current_time,
                    'last_seen': current_time,
                    'packet_count': 1,
                    'bytes_transferred': packet_info['packet_size'],
                    'status': 'active'
                }
            
            # Cleanup old flows periodically
            self._cleanup_old_flows()
            
        except Exception as e:
            logger.error(f"Error updating flow session: {e}")
    
    def _create_flow_id(self, packet_info: Dict[str, Any]) -> str:
        """Create unique flow identifier."""
        src_ip = packet_info.get('src_ip', '')
        dst_ip = packet_info.get('dst_ip', '')
        src_port = packet_info.get('src_port', 0)
        dst_port = packet_info.get('dst_port', 0)
        protocol = packet_info.get('protocol_name', '')
        
        # Create bidirectional flow ID (normalize direction)
        if src_ip < dst_ip or (src_ip == dst_ip and src_port < dst_port):
            flow_key = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{protocol}"
        else:
            flow_key = f"{dst_ip}:{dst_port}-{src_ip}:{src_port}-{protocol}"
        
        return hashlib.md5(flow_key.encode()).hexdigest()
    
    def _cleanup_old_flows(self):
        """Remove old inactive flows."""
        current_time = datetime.utcnow()
        flows_to_remove = []
        
        for flow_id, flow in self.active_flows.items():
            time_diff = (current_time - flow['last_seen']).total_seconds()
            if time_diff > self.flow_timeout:
                flows_to_remove.append(flow_id)
                
                # Store completed flow to database
                try:
                    with get_db_session() as session:
                        flow_record = FlowSession(
                            session_id=flow['session_id'],
                            src_ip=flow['src_ip'],
                            dst_ip=flow['dst_ip'],
                            src_port=flow['src_port'],
                            dst_port=flow['dst_port'],
                            protocol=flow['protocol'],
                            start_time=flow['start_time'],
                            end_time=flow['last_seen'],
                            duration=time_diff,
                            packet_count=flow['packet_count'],
                            bytes_transferred=flow['bytes_transferred'],
                            status='timeout'
                        )
                        session.add(flow_record)
                        session.commit()
                except Exception as e:
                    logger.error(f"Error storing flow session: {e}")
        
        # Remove old flows from memory
        for flow_id in flows_to_remove:
            del self.active_flows[flow_id]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get capture statistics."""
        stats = self.stats.copy()
        stats['active_flows'] = len(self.active_flows)
        stats['queue_size'] = self.packet_queue.qsize()
        
        if stats['start_time']:
            runtime = (datetime.utcnow() - stats['start_time']).total_seconds()
            stats['runtime_seconds'] = runtime
            stats['packets_per_second'] = stats['packets_captured'] / runtime if runtime > 0 else 0
        
        return stats