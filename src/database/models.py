"""Database models for Network Intelligence Packet Inspector."""

from sqlalchemy import (
    Column, Integer, String, DateTime, Float, Boolean, Text, 
    ForeignKey, Index, BigInteger
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class PacketCapture(Base):
    """Raw packet capture data."""
    __tablename__ = 'packet_captures'
    
    id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    src_ip = Column(String(45), index=True)  # IPv6 support
    dst_ip = Column(String(45), index=True)
    src_port = Column(Integer, index=True)
    dst_port = Column(Integer, index=True)
    protocol = Column(String(10), index=True)
    packet_size = Column(Integer)
    ttl = Column(Integer)
    flags = Column(String(20))
    payload_size = Column(Integer)
    interface = Column(String(50))
    
    # Relationships
    flow_sessions = relationship("FlowSession", back_populates="packets")
    
    __table_args__ = (
        Index('idx_packet_time_src', 'timestamp', 'src_ip'),
        Index('idx_packet_time_dst', 'timestamp', 'dst_ip'),
        Index('idx_packet_ports', 'src_port', 'dst_port'),
    )


class FlowSession(Base):
    """Network flow sessions."""
    __tablename__ = 'flow_sessions'
    
    id = Column(BigInteger, primary_key=True)
    session_id = Column(String(128), unique=True, index=True)
    src_ip = Column(String(45), index=True)
    dst_ip = Column(String(45), index=True)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String(10))
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    end_time = Column(DateTime)
    duration = Column(Float)  # seconds
    packet_count = Column(Integer, default=0)
    bytes_transferred = Column(BigInteger, default=0)
    status = Column(String(20), default='active')  # active, closed, timeout
    
    # Relationships
    packets = relationship("PacketCapture", back_populates="flow_sessions")
    security_events = relationship("SecurityEvent", back_populates="flow_session")


class NetworkHost(Base):
    """Discovered network hosts."""
    __tablename__ = 'network_hosts'
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(45), unique=True, index=True)
    hostname = Column(String(255))
    mac_address = Column(String(17))
    vendor = Column(String(100))
    os_family = Column(String(50))
    os_version = Column(String(100))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True)
    open_ports = Column(Text)  # JSON string of open ports
    services = Column(Text)    # JSON string of discovered services
    
    # Relationships
    bandwidth_stats = relationship("BandwidthStats", back_populates="host")
    security_events = relationship("SecurityEvent", back_populates="host")


class BandwidthStats(Base):
    """Bandwidth usage statistics."""
    __tablename__ = 'bandwidth_stats'
    
    id = Column(BigInteger, primary_key=True)
    host_id = Column(Integer, ForeignKey('network_hosts.id'), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    bytes_sent = Column(BigInteger, default=0)
    bytes_received = Column(BigInteger, default=0)
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    top_protocols = Column(Text)  # JSON string
    top_destinations = Column(Text)  # JSON string
    
    # Relationships
    host = relationship("NetworkHost", back_populates="bandwidth_stats")
    
    __table_args__ = (
        Index('idx_bandwidth_host_time', 'host_id', 'timestamp'),
    )


class SecurityEvent(Base):
    """Security-related events and alerts."""
    __tablename__ = 'security_events'
    
    id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(50), index=True)  # port_scan, ddos, suspicious_traffic
    severity = Column(String(20), index=True)    # low, medium, high, critical
    source_ip = Column(String(45), index=True)
    target_ip = Column(String(45))
    description = Column(Text)
    details = Column(Text)  # JSON string with additional details
    status = Column(String(20), default='new')  # new, investigating, resolved, false_positive
    
    # Foreign keys
    host_id = Column(Integer, ForeignKey('network_hosts.id'))
    flow_session_id = Column(BigInteger, ForeignKey('flow_sessions.id'))
    
    # Relationships
    host = relationship("NetworkHost", back_populates="security_events")
    flow_session = relationship("FlowSession", back_populates="security_events")


class PerformanceMetrics(Base):
    """Network performance metrics."""
    __tablename__ = 'performance_metrics'
    
    id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    interface = Column(String(50), index=True)
    total_bandwidth = Column(Float)  # Mbps
    utilization_percent = Column(Float)
    packet_loss_percent = Column(Float)
    latency_avg = Column(Float)  # milliseconds
    latency_max = Column(Float)
    jitter = Column(Float)
    error_count = Column(Integer)
    retransmission_count = Column(Integer)
    
    __table_args__ = (
        Index('idx_perf_interface_time', 'interface', 'timestamp'),
    )


class AlertRules(Base):
    """Configurable alert rules."""
    __tablename__ = 'alert_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    rule_type = Column(String(50))  # bandwidth, security, performance
    condition = Column(Text)  # JSON string with rule conditions
    threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemConfig(Base):
    """System configuration settings."""
    __tablename__ = 'system_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, index=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """System audit log."""
    __tablename__ = 'audit_log'
    
    id = Column(BigInteger, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    action = Column(String(100), index=True)
    user = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(45))