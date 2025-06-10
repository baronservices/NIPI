#!/usr/bin/env python3
"""Simple HTTP server for NIPI demo."""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_demo():
    """Serve the NIPI demo on localhost."""
    port = 8000
    
    # Change to the demo directory
    os.chdir(Path(__file__).parent)
    
    # Create simple handler
    class DemoHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.path = '/nipi_demo.html'
            return super().do_GET()
    
    try:
        with socketserver.TCPServer(("", port), DemoHandler) as httpd:
            print(f"🚀 NIPI Demo Server starting on http://localhost:{port}")
            print(f"📱 Access the demo at: http://localhost:{port}")
            print("🛑 Press Ctrl+C to stop the server")
            print()
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{port}')
            except:
                pass
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Demo server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Try a different port or stop other services.")
        else:
            print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    serve_demo()