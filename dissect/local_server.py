#!/usr/bin/env python3
"""
Enhanced Local Server for PDF Extractor
Serves the HTML report and images with advanced features and JSON support
"""

import argparse
import http.server
import json
import mimetypes
import os
import socketserver
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote


class EnhancedCORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Enhanced HTTP request handler with CORS headers and better file handling"""

    def __init__(self, *args, **kwargs):
        # Add support for additional MIME types
        mimetypes.add_type('application/json', '.json')
        mimetypes.add_type('image/webp', '.webp')
        mimetypes.add_type('text/javascript', '.js')
        mimetypes.add_type('text/css', '.css')
        super().__init__(*args, **kwargs)

    def end_headers(self):
        """Add CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        
        # Add caching headers based on file type
        try:
            if hasattr(self, 'path') and self.path:
                if self.path.endswith(('.html', '.json')):
                    # No cache for HTML and JSON files
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')
                elif self.path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                    # Cache images for 1 hour
                    self.send_header('Cache-Control', 'public, max-age=3600')
                elif self.path.endswith(('.css', '.js')):
                    # Cache static assets for 1 day
                    self.send_header('Cache-Control', 'public, max-age=86400')
                else:
                    # Default: no cache
                    self.send_header('Cache-Control', 'no-cache')
            else:
                # Default: no cache
                self.send_header('Cache-Control', 'no-cache')
        except Exception as e:
            # Fallback if path processing fails
            self.send_header('Cache-Control', 'no-cache')
            print(f"Warning: Could not set cache headers: {e}")
            
        super().end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Enhanced GET handler with better logging and error handling"""
        # Decode URL path safely
        try:
            path = unquote(self.path)
        except Exception as e:
            print(f"Error decoding path {self.path}: {e}")
            path = self.path

        # Log the request
        timestamp = datetime.now().strftime("%H:%M:%S")
        client_ip = self.client_address[0]
        print(f"[{timestamp}] {client_ip} - GET {path}")

        # Handle special endpoints
        if path == '/api/status':
            self.send_api_status()
            return
        elif path == '/api/reports':
            self.send_reports_list()
            return
        elif path == '/api/pages' and self.command == 'GET':
            self.send_pages_list()
            return
        elif path.startswith('/api/health'):
            self.send_health_check()
            return

        # Handle file not found gracefully
        try:
            # Clean up the path to handle problematic characters
            if path.startswith('/'):
                path = path[1:]  # Remove leading slash
            
            # Check if file exists before trying to serve
            if path and not os.path.exists(path):
                # Try to find the file with a more tolerant approach
                possible_paths = [
                    path,
                    path.replace('%20', ' '),  # Handle URL encoded spaces
                    path.replace('%5B', '[').replace('%5D', ']'),  # Handle encoded brackets
                    unquote(path),  # Full URL decode
                ]
                
                found_path = None
                for possible_path in possible_paths:
                    if os.path.exists(possible_path):
                        found_path = possible_path
                        break
                
                if found_path:
                    # Update the path to the found file
                    self.path = '/' + found_path if not found_path.startswith('/') else found_path
                else:
                    self.send_error(404, f"File not found: {path}")
                    return
            
            # Handle regular file requests
            super().do_GET()
            
        except FileNotFoundError:
            self.send_error(404, f"File not found: {path}")
        except UnicodeDecodeError as e:
            print(f"Unicode error with path {path}: {e}")
            self.send_error(400, f"Invalid path encoding: {path}")
        except Exception as e:
            print(f"Error serving {path}: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, f"Server error: {str(e)}")

    def guess_type(self, path):
        """Enhanced MIME type guessing with better error handling"""
        try:
            mimetype, encoding = super().guess_type(path)
        except (ValueError, TypeError) as e:
            # Fallback for problematic paths
            print(f"Warning: Could not guess MIME type for {path}: {e}")
            mimetype, encoding = 'application/octet-stream', None
        
        # Handle special cases
        if path.endswith('.json'):
            return 'application/json', encoding
        elif path.endswith('.webp'):
            return 'image/webp', encoding
        elif path.endswith('.svg'):
            return 'image/svg+xml', encoding
        elif path.endswith('.html'):
            return 'text/html', encoding
        elif path.endswith(('.jpg', '.jpeg')):
            return 'image/jpeg', encoding
        elif path.endswith('.png'):
            return 'image/png', encoding
        elif path.endswith('.gif'):
            return 'image/gif', encoding
        elif path.endswith('.css'):
            return 'text/css', encoding
        elif path.endswith('.js'):
            return 'text/javascript', encoding
            
        return mimetype or 'application/octet-stream', encoding

    def send_api_status(self):
        """Send server status as JSON"""
        # Get system information
        current_dir = Path('.').absolute()
        html_files = list(current_dir.glob("*_report.html"))
        json_files = list(current_dir.glob("*_pages.json"))
        image_dirs = [d for d in current_dir.iterdir() if d.is_dir() and d.name == 'images']
        
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'server': 'Enhanced PDF Extractor Server',
            'version': '2.1',
            'directory': str(current_dir),
            'files': {
                'html_reports': len(html_files),
                'json_data': len(json_files),
                'image_directories': len(image_dirs)
            },
            'features': [
                'CORS enabled',
                'Enhanced MIME types',
                'JSON data serving',
                'Auto-refresh support',
                'Lazy loading support',
                'Health check endpoint',
                'Settings persistence'
            ],
            'endpoints': [
                '/api/status',
                '/api/reports',
                '/api/pages',
                '/api/health'
            ]
        }

        response = json.dumps(status, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def send_health_check(self):
        """Send health check response"""
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time(),
            'memory_usage': 'available',  # Could add actual memory info if needed
            'disk_space': 'available'     # Could add actual disk info if needed
        }
        
        response = json.dumps(health, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def send_pages_list(self):
        """Send list of available page data files"""
        try:
            current_dir = Path('.')
            json_files = list(current_dir.glob("*_pages.json"))
            
            pages_info = []
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    pages_info.append({
                        'filename': json_file.name,
                        'basename': json_file.stem.replace('_pages', ''),
                        'total_pages': len(data),
                        'size': json_file.stat().st_size,
                        'modified': datetime.fromtimestamp(json_file.stat().st_mtime).isoformat(),
                        'pages': list(data.keys())
                    })
                except Exception as e:
                    pages_info.append({
                        'filename': json_file.name,
                        'error': str(e)
                    })
            
            response_data = {
                'pages_files': pages_info,
                'total_files': len(pages_info),
                'server_time': datetime.now().isoformat()
            }
            
            response = json.dumps(response_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            
        except Exception as e:
            error_response = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            response = json.dumps(error_response, indent=2).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

    def send_reports_list(self):
        """Send list of available reports as JSON"""
        try:
            html_files = list(Path('.').glob("*_report.html"))
            json_files = list(Path('.').glob("*_pages.json"))

            reports = []
            for html_file in html_files:
                # Find corresponding JSON file
                base_name = html_file.stem.replace('_report', '')
                pages_json_file = Path(f"{base_name}_pages.json")
                data_json_file = Path(f"{base_name}_data.json")

                report_info = {
                    'name': base_name,
                    'html_file': html_file.name,
                    'pages_json_file': pages_json_file.name if pages_json_file.exists() else None,
                    'data_json_file': data_json_file.name if data_json_file.exists() else None,
                    'html_size': html_file.stat().st_size,
                    'modified': datetime.fromtimestamp(html_file.stat().st_mtime).isoformat(),
                    'has_lazy_loading': pages_json_file.exists()
                }

                # Add metadata from pages JSON if available
                if pages_json_file.exists():
                    try:
                        with open(pages_json_file, 'r', encoding='utf-8') as f:
                            pages_data = json.load(f)
                            report_info.update({
                                'total_pages': len(pages_data),
                                'pages_json_size': pages_json_file.stat().st_size
                            })
                    except Exception as e:
                        report_info['pages_json_error'] = str(e)

                # Add metadata from data JSON if available
                if data_json_file.exists():
                    try:
                        with open(data_json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            report_info.update({
                                'pages': data.get('pages', 0),
                                'images': len(data.get('images', [])),
                                'extraction_time': data.get('extraction_time', ''),
                                'errors': len(data.get('errors', []))
                            })
                    except Exception as e:
                        report_info['data_json_error'] = str(e)

                reports.append(report_info)

            response_data = {
                'reports': reports,
                'total_reports': len(reports),
                'server_time': datetime.now().isoformat(),
                'features_enabled': {
                    'lazy_loading': any(r.get('has_lazy_loading', False) for r in reports),
                    'ai_analysis': True,  # Always available if API key is provided
                    'settings_persistence': True,
                    'modal_viewer': True
                }
            }

            response = json.dumps(response_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        except Exception as e:
            error_response = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            response = json.dumps(error_response, indent=2).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

    def log_message(self, format, *args):
        """Override to reduce verbose logging"""
        # Only log errors and important requests, not every successful request
        if not any(code in str(args) for code in ['200', '304']):
            super().log_message(format, *args)


def find_extraction_directories():
    """Find directories that look like extraction output"""
    current_dir = Path('.')
    extraction_dirs = []

    # Look for directories ending with '_extracted'
    for item in current_dir.iterdir():
        if item.is_dir() and item.name.endswith('_extracted'):
            extraction_dirs.append(item)

    # Also check if current directory has HTML reports
    html_files = list(current_dir.glob("*_report.html"))
    if html_files:
        extraction_dirs.append(current_dir)

    return extraction_dirs


def find_html_files(directory):
    """Find HTML files in the directory with enhanced information"""
    html_files = list(Path(directory).glob("*_report.html"))

    file_info = []
    for html_file in html_files:
        info = {
            'path': html_file,
            'name': html_file.name,
            'size': html_file.stat().st_size,
            'modified': datetime.fromtimestamp(html_file.stat().st_mtime),
            'base_name': html_file.stem.replace('_report', '')
        }

        # Check for corresponding JSON and images directory
        pages_json_file = html_file.parent / f"{info['base_name']}_pages.json"
        data_json_file = html_file.parent / f"{info['base_name']}_data.json"
        images_dir = html_file.parent / "images"

        info['has_pages_json'] = pages_json_file.exists()
        info['has_data_json'] = data_json_file.exists()
        info['has_images'] = images_dir.exists()
        info['has_lazy_loading'] = pages_json_file.exists()

        if info['has_images']:
            info['image_count'] = len(list(images_dir.glob("*")))

        if info['has_pages_json']:
            try:
                with open(pages_json_file, 'r', encoding='utf-8') as f:
                    pages_data = json.load(f)
                    info['total_pages'] = len(pages_data)
            except:
                info['total_pages'] = 'unknown'

        file_info.append(info)

    return file_info


def print_server_info(port, directory, html_files):
    """Print enhanced server information"""
    print("=" * 70)
    print("🚀 Enhanced PDF Extractor Server v2.1")
    print("=" * 70)
    print(f"📁 Serving directory: {os.path.abspath(directory)}")
    print(f"🌐 Server URL: http://localhost:{port}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if html_files:
        print(f"\n📊 Available HTML reports ({len(html_files)}):")
        for file_info in html_files:
            print(f"   📄 {file_info['name']}")
            print(f"      └─ URL: http://localhost:{port}/{file_info['name']}")
            print(f"      └─ Size: {file_info['size']:,} bytes")
            print(f"      └─ Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")

            features = []
            if file_info['has_lazy_loading']:
                features.append("🔄 Lazy Loading")
            if file_info['has_data_json']:
                features.append("📊 Data JSON")
            if file_info['has_images']:
                features.append(f"🖼️ Images ({file_info.get('image_count', 0)})")
            
            if features:
                print(f"      └─ Features: {', '.join(features)}")
            
            if file_info.get('total_pages'):
                print(f"      └─ Pages: {file_info['total_pages']}")
            print()
    else:
        print("\n⚠️  No HTML report files found in current directory.")
        print("   Make sure you're in the correct output directory.")

    print("\n🔧 API Endpoints:")
    print(f"   📊 Status: http://localhost:{port}/api/status")
    print(f"   📋 Reports: http://localhost:{port}/api/reports")
    print(f"   📄 Pages: http://localhost:{port}/api/pages")
    print(f"   ❤️  Health: http://localhost:{port}/api/health")

    print("\n💡 New Features:")
    print("   ✅ Lazy loading with chunked page rendering")
    print("   ✅ Settings persistence with localStorage")
    print("   ✅ Auto-scroll loading with intersection observer")
    print("   ✅ Enhanced CORS and caching headers")
    print("   ✅ JSON API for page data")
    print("   ✅ Health check endpoints")
    print("   ✅ Improved error handling")

    print("\n⌨️  Commands & Shortcuts:")
    print("   🛑 Press Ctrl+C to stop the server")
    print("   🔄 Refresh browser to see changes")
    print("   ⚙️  ESC - Close modals/settings")
    print("   💾 Ctrl+S - Save settings")
    print("   📄 Ctrl+L - Load more pages")
    print("=" * 70)


def auto_detect_directory():
    """Auto-detect the best directory to serve"""
    extraction_dirs = find_extraction_directories()

    if not extraction_dirs:
        return "."

    # Prefer directories with the most recent HTML files
    best_dir = None
    latest_time = 0

    for ext_dir in extraction_dirs:
        html_files = find_html_files(ext_dir)
        if html_files:
            latest_file_time = max(f['modified'].timestamp() for f in html_files)
            if latest_file_time > latest_time:
                latest_time = latest_file_time
                best_dir = ext_dir

    return str(best_dir) if best_dir else "."


def start_server(directory=".", port=9999, open_browser=True, auto_detect=False):
    """Start the enhanced local server"""

    # Auto-detect directory if requested
    if auto_detect:
        detected_dir = auto_detect_directory()
        if detected_dir != "." and os.path.exists(detected_dir):
            print(f"🔍 Auto-detected extraction directory: {detected_dir}")
            directory = detected_dir

    # Validate directory
    if not os.path.exists(directory):
        print(f"❌ Error: Directory '{directory}' does not exist.")
        return False

    # Change to the specified directory
    original_dir = os.getcwd()
    os.chdir(directory)

    try:
        # Find HTML files with enhanced info
        html_files = find_html_files(".")

        # Print server information
        print_server_info(port, directory, html_files)

        # Open browser if requested and files are available
        if open_browser and html_files:
            # Open the most recent HTML file
            latest_file = max(html_files, key=lambda x: x['modified'])
            url = f"http://localhost:{port}/{latest_file['name']}"
            print(f"\n🌐 Opening browser to: {url}")

            # Delay to let server start
            import threading
            def delayed_open():
                time.sleep(1.5)  # Slightly longer delay for enhanced server
                webbrowser.open(url)

            threading.Thread(target=delayed_open).start()

        # Start the server with enhanced handler
        print(f"\n🟢 Server starting on http://localhost:{port}")
        print("   Lazy loading and enhanced features enabled!")
        
        with socketserver.TCPServer(("", port), EnhancedCORSHTTPRequestHandler) as httpd:
            print(f"🚀 Server is now running and ready to serve requests")
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user.")
        return True
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use.")
            print(f"💡 Try a different port: python local_server.py --port {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Return to original directory
        os.chdir(original_dir)


def main():
    """Main function with enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description="Enhanced local server for PDF Extractor reports with lazy loading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python local_server.py                          # Serve current directory
  python local_server.py -d output_folder        # Serve specific directory
  python local_server.py --auto-detect           # Auto-detect extraction directory
  python local_server.py --port 8080             # Use custom port
  python local_server.py --no-browser            # Don't open browser
  python local_server.py --list-dirs             # List available directories
        """
    )

    parser.add_argument("--directory", "-d", default=".",
                        help="Directory to serve (default: current directory)")
    parser.add_argument("--port", "-p", type=int, default=9999,
                        help="Port to serve on (default: 9999)")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't automatically open browser")
    parser.add_argument("--auto-detect", "-a", action="store_true",
                        help="Auto-detect extraction output directory")
    parser.add_argument("--list-dirs", action="store_true",
                        help="List potential extraction directories and exit")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")

    args = parser.parse_args()

    # Handle list directories option
    if args.list_dirs:
        extraction_dirs = find_extraction_directories()
        if extraction_dirs:
            print("🔍 Found extraction directories:")
            for i, ext_dir in enumerate(extraction_dirs, 1):
                html_files = find_html_files(ext_dir)
                lazy_files = len([f for f in html_files if f.get('has_lazy_loading', False)])
                print(f"  {i}. {ext_dir} ({len(html_files)} HTML files, {lazy_files} with lazy loading)")
                
                for file_info in html_files[:3]:  # Show first 3 files
                    features = []
                    if file_info.get('has_lazy_loading'):
                        features.append("Lazy")
                    if file_info.get('has_images'):
                        features.append(f"{file_info.get('image_count', 0)} imgs")
                    
                    feature_str = f" [{', '.join(features)}]" if features else ""
                    print(f"     - {file_info['name']}{feature_str}")
                
                if len(html_files) > 3:
                    print(f"     ... and {len(html_files) - 3} more files")
                print()
        else:
            print("❌ No extraction directories found.")
        return

    # Enable verbose logging if requested
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    # Start the server
    success = start_server(
        directory=args.directory,
        port=args.port,
        open_browser=not args.no_browser,
        auto_detect=args.auto_detect
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()