#!/usr/bin/env python3
"""Database initialization script for NIPI."""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database.connection import init_database
from database.models import SystemConfig
import argparse


def populate_default_config():
    """Populate database with default configuration values."""
    from database.connection import db_manager
    
    default_configs = [
        {
            'key': 'capture.interface',
            'value': 'auto',
            'description': 'Default network interface for packet capture'
        },
        {
            'key': 'capture.buffer_size',
            'value': '1024',
            'description': 'Packet capture buffer size'
        },
        {
            'key': 'analysis.retention_days',
            'value': '30',
            'description': 'Number of days to retain packet data'
        },
        {
            'key': 'security.enable_threat_detection',
            'value': 'true',
            'description': 'Enable automatic threat detection'
        },
        {
            'key': 'web.refresh_interval',
            'value': '30',
            'description': 'Dashboard refresh interval in seconds'
        }
    ]
    
    if db_manager:
        with db_manager.get_session() as session:
            for config in default_configs:
                existing = session.query(SystemConfig).filter_by(key=config['key']).first()
                if not existing:
                    new_config = SystemConfig(
                        key=config['key'],
                        value=config['value'],
                        description=config['description']
                    )
                    session.add(new_config)
    
    print("Default configuration values added to database")


def main():
    """Main initialization function."""
    parser = argparse.ArgumentParser(description="Initialize NIPI database")
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation of database (WARNING: destroys existing data)'
    )
    
    args = parser.parse_args()
    
    try:
        print("Initializing Network Intelligence Packet Inspector database...")
        
        # Initialize database
        db_manager = init_database(args.config)
        
        if args.force:
            print("WARNING: Force flag specified, dropping existing tables...")
            db_manager.drop_tables()
            db_manager.create_tables()
            print("Database tables recreated")
        else:
            print("Database tables created/verified")
        
        # Populate default configuration
        populate_default_config()
        
        print("Database initialization completed successfully!")
        print("You can now start the NIPI application with: python src/main.py")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()