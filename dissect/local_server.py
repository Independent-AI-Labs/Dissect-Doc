#!/usr/bin/env python3
"""
Simple Local Server for PDF Extractor
Serves the HTML report and images to avoid CORS issues
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path
import argparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers"""
    
    def end_headers(self):
        """Add CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.end_headers()

def find_html_files(directory):
    """Find HTML files in the directory"""
    html_files = list(Path(directory).glob("*_report.html"))
    return html_files

def start_server(directory=".", port=9999, open_browser=True):
    """Start the local server"""
    
    # Change to the specified directory
    os.chdir(directory)
    
    # Find HTML files
    html_files = find_html_files(".")
    
    print(f"Starting local server in: {os.getcwd()}")
    print(f"Server URL: http://localhost:{port}")
    
    if html_files:
        print("\nAvailable HTML reports:")
        for html_file in html_files:
            print(f"  - http://localhost:{port}/{html_file.name}")
        
        if open_browser and html_files:
            # Open the first HTML file found
            url = f"http://localhost:{port}/{html_files[0].name}"
            print(f"\nOpening browser to: {url}")
            webbrowser.open(url)
    else:
        print("\nNo HTML report files found in current directory.")
        print("Make sure you're in the correct output directory.")
    
    # Start the server
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"\nServer running on port {port}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nPort {port} is already in use. Try a different port:")
            print(f"python local_server.py --port {port + 1}")
        else:
            print(f"Error starting server: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Start local server for PDF Extractor reports")
    parser.add_argument("--directory", "-d", default="./pdf_extraction_output",
                       help="Directory to serve (default: current directory)")
    parser.add_argument("--port", "-p", type=int, default=9999,
                       help="Port to serve on (default: 9999)")
    parser.add_argument("--no-browser", action="store_true",
                       help="Don't automatically open browser")
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        sys.exit(1)
    
    start_server(
        directory=args.directory,
        port=args.port,
        open_browser=not args.no_browser
    )

if __name__ == "__main__":
    main()
