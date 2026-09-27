"""Lightweight web server for real-time Vesper workflow visualization.

Uses Python's http.server with Server-Sent Events (SSE) for real-time updates.
Auto-opens browser on start. System preference for light/dark mode.
"""
import http.server
import json
import os
import socket
import socketserver
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from queue import Queue
from urllib.parse import parse_qs, urlparse


class SSEHandler:
    """Manages Server-Sent Events connections for real-time updates."""
    
    def __init__(self):
        self.clients = []
        self.events = []
        self.lock = threading.Lock()
    
    def add_client(self, client_queue):
        with self.lock:
            self.clients.append(client_queue)
            for message in self.events:
                client_queue.put(message)
    
    def remove_client(self, client_queue):
        with self.lock:
            if client_queue in self.clients:
                self.clients.remove(client_queue)
    
    def broadcast(self, event_type, data):
        """Send an event to all connected clients."""
        message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        with self.lock:
            self.events.append(message)
            dead_clients = []
            for client_queue in self.clients:
                try:
                    client_queue.put(message)
                except:
                    dead_clients.append(client_queue)
            for client in dead_clients:
                self.clients.remove(client)


class VesperRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for Vesper web UI."""
    
    def __init__(self, *args, sse_handler=None, web_root=None, **kwargs):
        self.sse_handler = sse_handler
        self.web_root = Path(web_root) if web_root else Path.cwd()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # SSE endpoint for real-time updates
        if parsed.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            
            client_queue = Queue()
            self.sse_handler.add_client(client_queue)
            
            try:
                while True:
                    message = client_queue.get(timeout=30)
                    self.wfile.write(message.encode())
                    self.wfile.flush()
            except:
                pass
            finally:
                self.sse_handler.remove_client(client_queue)
            return
        
        # Serve static files from web_root
        if parsed.path == "/":
            file_path = self.web_root / "index.html"
        else:
            file_path = self.web_root / parsed.path.lstrip("/")
        
        if file_path.exists() and file_path.is_file():
            self.send_response(200)
            content_type = self._get_content_type(file_path)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")
    
    def _get_content_type(self, file_path):
        suffix = file_path.suffix.lower()
        types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
        }
        return types.get(suffix, "application/octet-stream")
    
    def log_message(self, format, *args):
        """Suppress default server logging for cleaner output."""
        pass


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


class VesperWebServer:
    """Manages the web server lifecycle and real-time event broadcasting."""
    
    def __init__(self, port=8080, web_root=None):
        self.port = self._find_available_port(port)
        self.web_root = Path(web_root) if web_root else Path.cwd()
        self.sse_handler = SSEHandler()
        self.server = None
        self.server_thread = None
        self.browser_opened = False
    
    def _find_available_port(self, start_port):
        """Find an available port starting from the given port."""
        import socket
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return start_port  # Fallback to original if all are busy
    
    def start(self):
        """Start the web server in a background thread."""
        handler = lambda *args, **kwargs: VesperRequestHandler(
            *args, sse_handler=self.sse_handler, web_root=self.web_root, **kwargs
        )
        self.server = ThreadingHTTPServer(("localhost", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
        # Auto-open browser after a short delay
        threading.Thread(target=self._delayed_browser_open, daemon=True).start()
        
        return f"http://localhost:{self.port}"
    
    def _delayed_browser_open(self):
        """Open browser after server is ready."""
        time.sleep(0.5)
        if not self.browser_opened:
            webbrowser.open(f"http://localhost:{self.port}")
            self.browser_opened = True
    
    def stop(self):
        """Stop the web server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
    
    def broadcast_stage(self, stage_name, status, data=None):
        """Broadcast a stage update to all connected clients."""
        event_data = {
            "stage": stage_name,
            "status": status,
            "timestamp": time.time(),
        }
        if data:
            event_data.update(data)
        self.sse_handler.broadcast("stage", event_data)
    
    def broadcast_complete(self, final_status, duration):
        """Broadcast workflow completion."""
        self.sse_handler.broadcast("complete", {
            "status": final_status,
            "duration": duration,
            "timestamp": time.time(),
        })
    
    def broadcast_diff(self, original_code, candidate_code):
        """Broadcast the diff between original and candidate code."""
        self.sse_handler.broadcast("diff", {
            "original": original_code,
            "candidate": candidate_code,
            "timestamp": time.time(),
        })
    
    def broadcast_error(self, error_message):
        """Broadcast an error."""
        self.sse_handler.broadcast("error", {
            "message": error_message,
            "timestamp": time.time(),
        })


def create_web_ui_files(web_root):
    """Validate the checked-in dashboard assets; never generate competing copies."""
    root = Path(web_root)
    missing = [name for name in ('index.html', 'styles.css', 'app.js') if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError('Missing dashboard assets: ' + ', '.join(missing))
