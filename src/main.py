#!/usr/bin/env python3
"""Main entry point for Network Intelligence Packet Inspector."""

import os
import sys
import argparse
import logging
import signal
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from web.app import NIPIWebApp
from database.connection import init_database


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/nipi.log')
        ]
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)


def check_privileges():
    """Check if running with sufficient privileges for packet capture."""
    if os.geteuid() != 0:
        print("WARNING: Packet capture requires root privileges.")
        print("Some features may not work properly without root access.")
        print("Consider running with: sudo python src/main.py")
        return False
    return True


def signal_handler(signum, frame):
    """Handle graceful shutdown."""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Network Intelligence Packet Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python src/main.py --host 0.0.0.0 --port 8080
  python src/main.py --config custom_config.yaml --debug
  python src/main.py --init-db-only
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        help='Host to bind web server to (overrides config)'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        help='Port to bind web server to (overrides config)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    parser.add_argument(
        '--init-db-only',
        action='store_true',
        help='Initialize database and exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Network Intelligence Packet Inspector v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Network Intelligence Packet Inspector...")
    
    # Check privileges
    has_root = check_privileges()
    if not has_root:
        logger.warning("Running without root privileges - packet capture may not work")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database(args.config)
        logger.info("Database initialized successfully")
        
        if args.init_db_only:
            logger.info("Database initialization complete. Exiting.")
            return
        
        # Create and run web application
        logger.info("Starting web application...")
        web_app = NIPIWebApp(args.config)
        
        # Override config with command line arguments
        host = args.host
        port = args.port
        debug = args.debug
        
        logger.info(f"Web server starting on {host or 'default'}:{port or 'default'}")
        logger.info("Access the application at: http://localhost:8080")
        logger.info("Press Ctrl+C to stop")
        
        web_app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Network Intelligence Packet Inspector stopped")


if __name__ == '__main__':
    main()