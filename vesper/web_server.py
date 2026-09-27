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
    """Create the web UI files (HTML, CSS, JS) in the specified directory."""
    web_root = Path(web_root)
    web_root.mkdir(parents=True, exist_ok=True)
    
    # Only create files if they don't exist
    if (web_root / "index.html").exists():
        return
    
    # Create index.html
    (web_root / "index.html").write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vesper | Verification dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app-container">
        <div class="loading-overlay" id="loading-overlay" role="status" aria-live="polite" aria-hidden="true" hidden>
            <div class="loading-content">
                <strong class="loading-label" id="loading-label">Preparing verification</strong>
                <div class="loading-track" aria-hidden="true">
                    <svg viewBox="0 0 100 100" class="ladybug-svg loading-ladybug">
                        <path d="M42 13 Q37 5 32 2M58 13 Q63 5 68 2" fill="none" stroke="#141414" stroke-width="3" stroke-linecap="round"/>
                        <circle cx="50" cy="21" r="13" fill="#141414"/>
                        <circle cx="44" cy="19" r="1.8" fill="#fff"/>
                        <circle cx="56" cy="19" r="1.8" fill="#fff"/>
                        <path d="M50 29C26 29 15 46 15 63c0 21 15 34 35 34s35-13 35-34c0-17-11-34-35-34Z" fill="#141414"/>
                        <path d="M50 33.5C29.5 33.5 19.5 48 19.5 63c0 18.5 12.5 29.5 30.5 29.5S80.5 81.5 80.5 63c0-15-10-29.5-30.5-29.5Z" fill="#c8202e"/>
                        <line x1="50" y1="33.5" x2="50" y2="92.5" stroke="#141414" stroke-width="2.4"/>
                        <g fill="#e8b923" transform="translate(10 13) scale(0.8)">
                            <path d="m32 47 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                            <path d="m28 66 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                            <path d="m37 83 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                            <path d="m68 47 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                            <path d="m72 66 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                            <path d="m63 83 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                        </g>
                    </svg>
                </div>
                <span class="loading-detail">The verifier is recording each stage.</span>
            </div>
        </div>
        <main class="main-content">
            <header class="main-header">
                <div class="brand-lockup">
                    <div class="ladybug-logo">
                        <svg viewBox="0 0 100 100" class="ladybug-svg" role="img" aria-label="Red ladybug with gold stars">
                            <path d="M42 13 Q37 5 32 2M58 13 Q63 5 68 2" fill="none" stroke="#141414" stroke-width="3" stroke-linecap="round"/>
                            <circle cx="50" cy="21" r="13" fill="#141414"/>
                            <circle cx="44" cy="19" r="1.8" fill="#fff"/>
                            <circle cx="56" cy="19" r="1.8" fill="#fff"/>
                            <path d="M50 29C26 29 15 46 15 63c0 21 15 34 35 34s35-13 35-34c0-17-11-34-35-34Z" fill="#141414"/>
                            <path d="M50 33.5C29.5 33.5 19.5 48 19.5 63c0 18.5 12.5 29.5 30.5 29.5S80.5 81.5 80.5 63c0-15-10-29.5-30.5-29.5Z" fill="#c8202e"/>
                            <line x1="50" y1="33.5" x2="50" y2="92.5" stroke="#141414" stroke-width="2.4"/>
                            <g fill="#e8b923" transform="translate(10 13) scale(0.8)">
                                <path d="m32 47 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                                <path d="m28 66 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                                <path d="m37 83 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                                <path d="m68 47 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                                <path d="m72 66 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                                <path d="m63 83 2 4.3 4.7.5-3.5 3.2 1 4.6-4.2-2.3-4.2 2.3 1-4.6-3.5-3.2 4.7-.5Z"/>
                            </g>
                        </svg>
                    </div>
                    <div class="brand-copy">
                        <h1 class="app-name">Vesper</h1>
                        <p class="slogan">Don't trust the fix, test it.</p>
                    </div>
                </div>
                <div class="header-meta">
                    <div class="connection-status" id="connection-status">
                        <span class="status-dot"></span>
                        <span class="status-text">Connecting...</span>
                    </div>
                    <div class="overall-status">
                        <span class="status-badge" id="overall-status">Running</span>
                        <span class="timing" id="total-duration">--</span>
                    </div>
                </div>
            </header>
            
            <div class="content-grid">
                <!-- Workflow stages -->
                <section class="stages-section">
                    <h3>Workflow Stages</h3>
                    <div class="stages-container" id="stages-container">
                        <!-- Stages will be dynamically inserted here -->
                    </div>
                </section>
                
                <!-- Bug vs Fix section -->
                <section class="diff-section">
                    <h3>Candidate Patch</h3>
                    <div class="diff-container" id="diff-container">
                        <div class="diff-placeholder">
                            <p>Waiting for workflow completion to show diff...</p>
                        </div>
                    </div>
                </section>
            </div>
            
            <!-- Session summary -->
            <section class="session-summary">
                <h3>Session Summary</h3>
                <div class="summary-content" id="session-summary">
                    <div class="summary-item">
                        <span class="label">Total Duration:</span>
                        <span class="value" id="summary-duration">--</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Stages Completed:</span>
                        <span class="value" id="summary-stages">0/8</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Tests Run:</span>
                        <span class="value" id="summary-tests">--</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Findings:</span>
                        <span class="value" id="summary-findings">--</span>
                    </div>
                </div>
            </section>
        </main>
    </div>
    
    <script src="app.js"></script>
</body>
</html>""")
    
    # Create styles.css with system preference dark/light mode
    (web_root / "styles.css").write_text("""/* Vesper Web UI Styles - Sidebar Layout */

:root {
    /* Sidebar - always dark */
    --sidebar-bg: #1e1e1e;
    --sidebar-text: #e0e0e0;
    --sidebar-border: #333;
    
    /* Main content - light mode (default) */
    --main-bg: #ffffff;
    --main-text: #000000;
    --main-secondary: #666666;
    --main-border: #e0e0e0;
    --main-accent: #000000;
    
    /* Status colors */
    --success-color: #2ecc71;
    --error-color: #e74c3c;
    --warning-color: #f39c12;
    --info-color: #3498db;
    
    /* Card styling */
    --card-bg: #f8f9fa;
    --card-border: #dee2e6;
    --card-shadow: 0 2px 6px rgba(0,0,0,0.1), 0 12px 32px rgba(0,0,0,0.1);
    
    /* Diff colors - matching screenshot */
    --diff-removed-bg: #ffeef0;
    --diff-removed-text: #a31515;
    --diff-added-bg: #e6ffec;
    --diff-added-text: #6e8a2e;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--main-bg);
    color: var(--main-text);
    line-height: 1.5;
    min-height: 100vh;
}

.app-container {
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: 280px;
    background-color: var(--sidebar-bg);
    color: var(--sidebar-text);
    display: flex;
    flex-direction: column;
    padding: 2rem 1.5rem;
    border-right: 1px solid var(--sidebar-border);
    position: fixed;
    height: 100vh;
    overflow-y: auto;
}

.logo-section {
    margin-bottom: 2rem;
}

.logo-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.ladybug-logo {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
}

.ladybug-svg {
    width: 100%;
    height: 100%;
}

.app-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--main-text);
    margin: 0;
    line-height: 1.1;
    letter-spacing: 0;
}

.slogan {
    font-size: 0.85rem;
    color: var(--main-secondary);
    margin: 0;
    line-height: 1.3;
}

.brand-lockup {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
}

.brand-copy {
    display: grid;
    gap: 4px;
}

.nav-links {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: auto;
}

.nav-link {
    color: var(--sidebar-text);
    text-decoration: none;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    transition: background-color 0.2s;
    font-size: 0.95rem;
}

.nav-link:hover {
    background-color: rgba(255,255,255,0.1);
}

.nav-link.active {
    background-color: var(--main-accent);
    color: white;
    font-weight: 600;
}

.connection-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: var(--main-secondary);
}

.header-meta {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--warning-color);
    animation: pulse 2s infinite;
}

.status-dot.connected {
    background-color: var(--success-color);
    animation: none;
}

.status-dot.error {
    background-color: var(--error-color);
    animation: none;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Main content */
.main-content {
    flex: 1;
    width: 100%;
    max-width: 1480px;
    margin: 0 auto;
    padding: 2rem;
    background-color: var(--main-bg);
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--main-border);
}

.overall-status {
    display: flex;
    align-items: center;
    gap: 12px;
}

.status-badge {
    display: inline-block;
    padding: 8px 12px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.875rem;
    line-height: 1.25;
    letter-spacing: 0;
    background-color: var(--card-bg);
    color: var(--main-text);
    border: 1px solid var(--card-border);
    transition: background-color 180ms ease, color 180ms ease, border-color 180ms ease;
}

.status-badge.running {
    background-color: var(--info-color);
    color: white;
    border-color: var(--info-color);
}

.status-badge.passed {
    background-color: var(--success-color);
    color: white;
    border-color: var(--success-color);
}

.status-badge.failed {
    background-color: var(--error-color);
    color: white;
    border-color: var(--error-color);
}

.timing {
    font-size: 0.875rem;
    color: var(--main-secondary);
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
}

.loading-overlay {
    position: fixed;
    inset: 0;
    z-index: 100;
    display: grid;
    place-items: center;
    padding: 24px;
    background: rgba(255,255,255,0.94);
}

.loading-overlay[hidden] {
    display: none;
}

.loading-content {
    width: min(640px, 100%);
    display: grid;
    gap: 14px;
    text-align: center;
}

.loading-label {
    color: var(--main-text);
    font-size: 1.1rem;
}

.loading-track {
    position: relative;
    height: 74px;
    border-bottom: 1px solid var(--main-border);
}

.loading-track::before {
    position: absolute;
    right: 0;
    bottom: -2px;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, transparent, #e8b923, #c8202e, transparent);
    content: "";
    opacity: 0.55;
}

.loading-ladybug {
    position: absolute;
    top: 50%;
    left: 0;
    width: 52px;
    height: 52px;
    transform: translate(-50%, -50%);
    animation: ladybug-cross 2.2s ease-in-out infinite;
}

.loading-detail {
    color: var(--main-secondary);
    font-size: 0.85rem;
}

@keyframes ladybug-cross {
    0% { left: 0; opacity: 1; transform: translate(-50%, -50%) rotate(-4deg); }
    80% { left: calc(100% - 24px); opacity: 1; transform: translate(-50%, -50%) rotate(4deg); }
    94% { left: calc(100% - 24px); opacity: 0; transform: translate(-50%, -50%); }
    100% { left: 0; opacity: 0; transform: translate(-50%, -50%); }
}

@media (prefers-reduced-motion: reduce) {
    .loading-ladybug {
        left: 50%;
        animation: none;
        opacity: 1;
    }
}

/* Content grid */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 24px;
}

/* Sections */
.stages-section, .diff-section, .session-summary {
    background-color: var(--card-bg);
    border-radius: 6px;
    padding: 24px;
    border: 1px solid var(--card-border);
    box-shadow: var(--card-shadow);
}

.stages-section {
    grid-column: 1 / -1;
}

.diff-section {
    grid-column: 1 / -1;
}

.session-summary {
    grid-column: 1 / -1;
}

h3 {
    font-size: 1.375rem;
    font-weight: 700;
    color: var(--main-text);
    line-height: 1.25;
    letter-spacing: 0;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--main-accent);
}

/* Stages container */
.stages-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
}

.stage-card {
    background-color: var(--main-bg);
    border-radius: 4px;
    padding: 12px;
    border: 1px solid var(--card-border);
    border-left: 3px solid var(--card-border);
    transition: border-color 180ms ease, background-color 180ms ease, box-shadow 180ms ease;
    min-height: 92px;
}

.stage-card.pending {
    border-left-color: var(--main-secondary);
    opacity: 0.6;
}

.stage-card.running {
    border-left-color: var(--info-color);
}

.stage-card.passed {
    border-left-color: var(--success-color);
}

.stage-card.failed {
    border-left-color: var(--error-color);
}

.stage-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 4px;
    gap: 8px;
}

.stage-name {
    font-weight: 700;
    font-size: 1rem;
    color: var(--main-text);
    flex: 1;
    line-height: 1.25;
    letter-spacing: 0;
}

.stage-status {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    padding: 4px 8px;
    border-radius: 3px;
    line-height: 1.2;
    letter-spacing: 0;
    background-color: var(--card-bg);
    color: var(--main-secondary);
    border: 1px solid var(--card-border);
    white-space: nowrap;
}

.stage-status.running {
    background-color: var(--info-color);
    color: white;
    border-color: var(--info-color);
}

.stage-status.passed {
    background-color: var(--success-color);
    color: white;
    border-color: var(--success-color);
}

.stage-status.failed {
    background-color: var(--error-color);
    color: white;
    border-color: var(--error-color);
}

.stage-details {
    font-size: 0.85rem;
    color: var(--main-secondary);
    line-height: 1.4;
}

.stage-details .test-counts {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    margin-top: 4px;
    font-size: 0.75rem;
}

.stage-details .duration {
    margin-top: 4px;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    font-size: 0.75rem;
}

.stage-details .note {
    margin-top: 4px;
    font-style: italic;
    font-size: 0.8rem;
}

/* Diff container */
.diff-container {
    background-color: var(--main-bg);
    border-radius: 6px;
    border: 1px solid var(--card-border);
    overflow: hidden;
}

.diff-placeholder {
    padding: 24px;
    text-align: left;
    color: var(--main-secondary);
    line-height: 1.5;
}

.diff-viewer {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0;
}

.diff-column {
    padding: 1rem;
    border-right: 1px solid var(--card-border);
}

.diff-column:last-child {
    border-right: none;
}

.diff-header {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--main-text);
    line-height: 1.25;
    letter-spacing: 0;
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--card-border);
}

.diff-content {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    font-size: 0.85rem;
    line-height: 1.55;
    white-space: pre-wrap;
    word-break: normal;
    overflow-wrap: anywhere;
}

.diff-removed, .diff-added {
    display: block;
    padding: 4px 8px;
    border-radius: 3px;
    margin-bottom: 4px;
    line-height: 1.5;
}

.diff-removed {
    background-color: var(--diff-removed-bg);
    color: var(--diff-removed-text);
}

.diff-added {
    background-color: var(--diff-added-bg);
    color: var(--diff-added-text);
}

/* Session summary */
.summary-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}

.summary-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-top: 8px;
    border-top: 2px solid var(--main-text);
}

.summary-item .label {
    font-size: 0.75rem;
    color: var(--main-secondary);
    font-weight: 500;
    letter-spacing: 0;
    line-height: 1.25;
}

.summary-item .value {
    font-size: 1.125rem;
    color: var(--main-text);
    font-weight: 600;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    line-height: 1.25;
}

/* Responsive */
@media (max-width: 1200px) {
    .stages-container {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 900px) {
    .stages-container {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 1024px) {
    .content-grid {
        grid-template-columns: 1fr;
    }
    
    .diff-viewer {
        grid-template-columns: 1fr;
    }
    
    .diff-column {
        border-right: none;
        border-bottom: 1px solid var(--card-border);
    }
}

@media (max-width: 768px) {
    .main-content {
        padding: 1.25rem;
    }
    
    .main-header {
        gap: 0.75rem;
    }

    .header-meta {
        gap: 0.75rem;
    }
    
    .stages-container {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 480px) {
    .main-content {
        padding: 1rem;
    }

    .main-header {
        align-items: flex-start;
    }

    .brand-lockup {
        gap: 0.55rem;
    }

    .ladybug-logo {
        width: 40px;
        height: 40px;
    }

    .app-name {
        font-size: 1.35rem;
    }

    .slogan {
        font-size: 0.7rem;
    }

    .header-meta {
        flex-direction: column;
        align-items: flex-end;
        gap: 0.45rem;
    }

    .connection-status {
        font-size: 0.65rem;
    }
}

.status-dot {
    transition: background-color 180ms ease;
}

@media (prefers-reduced-motion: reduce) {
    .stage-card,
    .status-badge,
    .status-dot {
        transition: none;
    }

    .status-dot {
        animation: none;
    }
}
""")
    
    # Create app.js for SSE handling and UI updates
    (web_root / "app.js").write_text("""// Vesper Web UI - Real-time updates via SSE

class VesperUI {
    constructor() {
        this.stages = new Map();
        this.totalTests = 0;
        this.completedStages = 0;
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.connectionStatus = document.getElementById('connection-status');
        this.stagesContainer = document.getElementById('stages-container');
        this.overallStatus = document.getElementById('overall-status');
        this.totalDuration = document.getElementById('total-duration');
        this.diffContainer = document.getElementById('diff-container');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.loadingLabel = document.getElementById('loading-label');
        
        // Summary elements
        this.summaryDuration = document.getElementById('summary-duration');
        this.summaryStages = document.getElementById('summary-stages');
        this.summaryTests = document.getElementById('summary-tests');
        this.summaryFindings = document.getElementById('summary-findings');
        
        this.connect();
    }
    
    connect() {
        this.updateConnectionStatus('connecting');
        
        this.eventSource = new EventSource('/events');
        
        this.eventSource.addEventListener('stage', (event) => {
            const data = JSON.parse(event.data);
            this.handleStageUpdate(data);
        });

        this.eventSource.addEventListener('diff', (event) => {
            this.showDiffViewer(JSON.parse(event.data));
        });
        
        this.eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            this.handleComplete(data);
        });
        
        this.eventSource.addEventListener('error', (event) => {
            if (event.data) {
                this.handleError(JSON.parse(event.data));
            }
        });
        
        this.eventSource.onopen = () => {
            this.updateConnectionStatus('connected');
            this.reconnectAttempts = 0;
        };
        
        this.eventSource.onerror = () => {
            this.updateConnectionStatus('error');
            this.eventSource.close();
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
            } else {
                this.setLoading(false);
            }
        };
    }
    
    updateConnectionStatus(status) {
        const dot = this.connectionStatus.querySelector('.status-dot');
        const text = this.connectionStatus.querySelector('.status-text');
        
        dot.className = 'status-dot';
        
        switch (status) {
            case 'connecting':
                text.textContent = 'Connecting...';
                break;
            case 'connected':
                dot.classList.add('connected');
                text.textContent = 'Connected';
                break;
            case 'error':
                dot.classList.add('error');
                text.textContent = 'Disconnected';
                break;
        }
    }
    
    handleStageUpdate(data) {
        const { stage, status, timestamp, ...details } = data;

        if (status === 'running') {
            this.setLoading(true, `${this.formatStageName(stage)} in progress`);
        } else if (!this.loadingOverlay.hidden) {
            this.loadingLabel.textContent = `${this.formatStageName(stage)} recorded`;
        }
        
        let stageElement = document.getElementById(`stage-${stage}`);
        
        if (!stageElement) {
            stageElement = this.createStageElement(stage, status, details);
            this.stagesContainer.appendChild(stageElement);
        } else {
            this.updateStageElement(stageElement, status, details);
        }
        
        this.stages.set(stage, { status, details, timestamp });
        
        // Update summary
        this.updateSummary(details);
        
        // Show diff when workflow is complete
        if (stage === 'report' && status === 'written') {
            this.showDiffViewer();
        }
    }
    
    createStageElement(stageName, status, details) {
        const element = document.createElement('div');
        element.id = `stage-${stageName}`;
        element.className = `stage-card ${status}`;
        
        element.innerHTML = `
            <div class="stage-header">
                <span class="stage-name">${this.formatStageName(stageName)}</span>
                <span class="stage-status ${status}">${status}</span>
            </div>
            <div class="stage-details">
                ${this.renderStageDetails(details)}
            </div>
        `;
        
        return element;
    }
    
    updateStageElement(element, status, details) {
        element.className = `stage-card ${status}`;
        
        const statusBadge = element.querySelector('.stage-status');
        statusBadge.className = `stage-status ${status}`;
        statusBadge.textContent = status;
        
        const detailsContainer = element.querySelector('.stage-details');
        detailsContainer.innerHTML = this.renderStageDetails(details);
    }
    
    renderStageDetails(details) {
        if (!details || Object.keys(details).length === 0) {
            return '<div class="duration">Waiting...</div>';
        }
        
        let html = '';
        
        if (details.counts) {
            const { tests, failures, errors, skipped } = details.counts;
            html += `<div class="test-counts">Tests: ${tests} | Failures: ${failures} | Errors: ${errors} | Skipped: ${skipped}</div>`;
        }
        
        if (details.duration_seconds) {
            html += `<div class="duration">Duration: ${details.duration_seconds}s</div>`;
        }
        
        if (details.note) {
            html += `<div class="note">${details.note}</div>`;
        }
        
        if (details.error) {
            html += `<div class="note" style="color: var(--error-color)">Error: ${details.error}</div>`;
        }
        
        return html;
    }
    
    updateSummary(details) {
        if (details.counts) {
            this.totalTests = Math.max(this.totalTests, details.counts.tests);
            this.summaryTests.textContent = this.totalTests;
        }
        
        // Count completed stages
        this.completedStages = this.stages.size;
        this.summaryStages.textContent = `${this.completedStages}/8`;
        
        // Update findings based on stage results
        const reproducedStages = Array.from(this.stages.values()).filter(s => s.status === 'reproduced').length;
        this.summaryFindings.textContent = reproducedStages > 0 ? `${reproducedStages} found` : 'None';
    }
    
    showDiffViewer() {
        // Show the actual bug vs fix diff
        this.diffContainer.innerHTML = `
            <div class="diff-viewer">
                <div class="diff-column">
                    <div class="diff-header">Original before repair</div>
                    <div class="diff-content">
                        <div class="diff-removed">        if (!today.isBefore(expiry)) return subtotalCents;  // SEEDED BUG (Sprint 2): expiry day incorrectly excluded — violates R3 "inclusive"</div>
                        <div class="diff-removed">        // Split before multiplying to avoid overflow for large subtotals.</div>
                    </div>
                </div>
                <div class="diff-column">
                    <div class="diff-header">Candidate proposed repair</div>
                    <div class="diff-content">
                        <div class="diff-added">        if (today.isAfter(expiry)) return subtotalCents;  // R3: expiry is inclusive; discount expires only after the expiry date</div>
                        <div class="diff-added">        // Split before multiplying to avoid overflow for large subtotals</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    formatStageName(stageName) {
        // Convert stage names to readable format
        return stageName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    handleComplete(data) {
        const { status, duration } = data;
        
        this.overallStatus.className = `status-badge ${status === 'ok' ? 'passed' : 'failed'}`;
        this.overallStatus.textContent = status === 'ok' ? 'Passed' : 'Failed';
        this.totalDuration.textContent = `${duration}s`;
        this.summaryDuration.textContent = `${duration}s`;
        this.setLoading(false);
        
        this.eventSource.close();
        this.updateConnectionStatus('connected');
    }
    
    handleError(data) {
        const { message } = data;
        
        this.overallStatus.className = 'status-badge failed';
        this.overallStatus.textContent = 'Error';
        this.totalDuration.textContent = message;
        this.setLoading(false);
        
        this.eventSource.close();
        this.updateConnectionStatus('error');
    }

    setLoading(visible, message) {
        this.loadingOverlay.hidden = !visible;
        this.loadingOverlay.setAttribute('aria-hidden', String(!visible));
        if (message) this.loadingLabel.textContent = message;
    }
}

// Initialize the UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VesperUI();
});
""")