#!/usr/bin/env python3
"""
Simple HTTP Server for SusuSave Landing Page
Serves the landing page with proper MIME types and PWA support
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
HOST = "0.0.0.0"

# Get the directory containing this script
WEB_DIR = Path(__file__).parent.absolute()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and routing"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)
    
    def end_headers(self):
        """Add custom headers for PWA support"""
        # Enable service worker
        self.send_header('Service-Worker-Allowed', '/')
        
        # Security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        
        # Cache control for different file types
        if self.path.endswith(('.html', '.json')):
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
        elif self.path.endswith(('.js', '.css')):
            self.send_header('Cache-Control', 'public, max-age=86400')  # 1 day
        elif self.path.endswith(('.svg', '.png', '.jpg', '.jpeg', '.webp')):
            self.send_header('Cache-Control', 'public, max-age=604800')  # 7 days
        
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests with routing support"""
        # Handle root path
        if self.path == '/':
            self.path = '/index.html'
        
        # Handle service worker
        if self.path == '/sw-landing.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.send_header('Service-Worker-Allowed', '/')
            self.end_headers()
            try:
                with open(WEB_DIR / 'sw-landing.js', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, 'Service Worker not found')
            return
        
        # Serve manifest.json with correct MIME type
        if self.path == '/manifest.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/manifest+json')
            self.end_headers()
            try:
                with open(WEB_DIR / 'manifest.json', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, 'Manifest not found')
            return
        
        # Default behavior for other files
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Custom log format with colors"""
        status_code = args[1] if len(args) > 1 else '000'
        
        # Color codes
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        RESET = '\033[0m'
        BLUE = '\033[94m'
        
        # Choose color based on status code
        if status_code.startswith('2'):
            color = GREEN
        elif status_code.startswith('3'):
            color = YELLOW
        elif status_code.startswith('4') or status_code.startswith('5'):
            color = RED
        else:
            color = RESET
        
        print(f"{BLUE}[{self.log_date_time_string()}]{RESET} "
              f"{color}{format % args}{RESET}")

def run_server():
    """Start the HTTP server"""
    # Change to web directory
    os.chdir(WEB_DIR)
    
    # Create server
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        print("\n" + "="*60)
        print("🚀 SusuSave Landing Page Server")
        print("="*60)
        print(f"\n✅ Server running at:")
        print(f"   🌐 Local:   http://localhost:{PORT}")
        print(f"   🌐 Network: http://{HOST}:{PORT}")
        print(f"\n📁 Serving directory: {WEB_DIR}")
        print(f"\n📱 PWA Features:")
        print(f"   ✓ Service Worker: /sw-landing.js")
        print(f"   ✓ Web Manifest:   /manifest.json")
        print(f"   ✓ Offline Support")
        print(f"   ✓ Install Prompt")
        print("\n💡 Tips:")
        print("   • Open in Chrome/Edge to see PWA install prompt")
        print("   • Check DevTools > Application > Service Workers")
        print("   • Press Ctrl+C to stop the server")
        print("\n" + "="*60 + "\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    run_server()

