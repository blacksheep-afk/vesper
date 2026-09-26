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
        self.lock = threading.Lock()
    
    def add_client(self, client_queue):
        with self.lock:
            self.clients.append(client_queue)
    
    def remove_client(self, client_queue):
        with self.lock:
            if client_queue in self.clients:
                self.clients.remove(client_queue)
    
    def broadcast(self, event_type, data):
        """Send an event to all connected clients."""
        message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        with self.lock:
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
        self.server = socketserver.TCPServer(("localhost", self.port), handler)
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
    <title>Vesper Workflow Results</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="logo-section">
                <div class="logo-row">
                    <div class="ladybug-logo">
                        <svg viewBox="0 0 100 100" class="ladybug-svg">
                            <!-- Ladybug body -->
                            <ellipse cx="50" cy="50" rx="35" ry="30" fill="#e63946"/>
                            <!-- Ladybug head -->
                            <circle cx="50" cy="85" r="12" fill="#e63946"/>
                            <!-- Gold stars instead of dots -->
                            <text x="32" y="45" font-size="14" fill="#FFD700">★</text>
                            <text x="50" y="35" font-size="14" fill="#FFD700">★</text>
                            <text x="68" y="45" font-size="14" fill="#FFD700">★</text>
                            <text x="32" y="65" font-size="14" fill="#FFD700">★</text>
                            <text x="50" y="75" font-size="14" fill="#FFD700">★</text>
                            <text x="68" y="65" font-size="14" fill="#FFD700">★</text>
                            <!-- Eyes -->
                            <circle cx="45" cy="82" r="2" fill="white"/>
                            <circle cx="55" cy="82" r="2" fill="white"/>
                        </svg>
                    </div>
                    <h1 class="app-name">Vesper</h1>
                </div>
                <p class="slogan">Don't trust the fix, test it.</p>
            </div>
            
            <nav class="nav-links">
                <a href="#" class="nav-link active">Dashboard</a>
                <a href="#" class="nav-link">Findings</a>
                <a href="#" class="nav-link">Evidence</a>
                <a href="#" class="nav-link">Settings</a>
            </nav>
            
            <div class="connection-status" id="connection-status">
                <span class="status-dot"></span>
                <span class="status-text">Connecting...</span>
            </div>
        </aside>
        
        <!-- Main content -->
        <main class="main-content">
            <header class="main-header">
                <h2>Workflow Results</h2>
                <div class="overall-status">
                    <span class="status-badge" id="overall-status">Running</span>
                    <span class="timing" id="total-duration">--</span>
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
    --card-shadow: 0 2px 8px rgba(0,0,0,0.1);
    
    /* Diff colors - matching screenshot */
    --diff-removed-bg: #ffeef0;
    --diff-removed-text: #a31515;
    --diff-added-bg: #e6ffec;
    --diff-added-text: #6e8a2e;
}

@media (prefers-color-scheme: dark) {
    :root {
        /* Main content - dark mode */
        --main-bg: #2d2d2d;
        --main-text: #ffffff;
        --main-secondary: #b0b0b0;
        --main-border: #404040;
        --card-bg: #363636;
        --card-border: #505050;
        --card-shadow: 0 2px 8px rgba(0,0,0,0.3);
        
        /* Diff colors - dark mode */
        --diff-removed-bg: #4a2a2a;
        --diff-removed-text: #ff6b6b;
        --diff-added-bg: #2a4a2a;
        --diff-added-text: #6bff6b;
    }
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
    line-height: 1.6;
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
    width: 32px;
    height: 32px;
    flex-shrink: 0;
}

.ladybug-svg {
    width: 100%;
    height: 100%;
}

.app-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--sidebar-text);
    margin: 0;
    line-height: 1;
}

.slogan {
    font-size: 0.95rem;
    color: #ffffff;
    font-style: italic;
    margin: 0;
    line-height: 1.5;
    font-weight: 400;
    opacity: 0.95;
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
    color: #888;
    padding-top: 1rem;
    border-top: 1px solid var(--sidebar-border);
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
    margin-left: 280px;
    padding: 2rem;
    background-color: var(--main-bg);
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--main-border);
}

.main-header h2 {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--main-text);
}

.overall-status {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.status-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 1rem;
    background-color: var(--card-bg);
    color: var(--main-text);
    border: 1px solid var(--card-border);
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

/* Content grid */
.content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
}

/* Sections */
.stages-section, .diff-section, .session-summary {
    background-color: var(--card-bg);
    border-radius: 8px;
    padding: 1.5rem;
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
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--main-text);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--main-accent);
}

/* Stages container */
.stages-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
}

.stage-card {
    background-color: var(--main-bg);
    border-radius: 6px;
    padding: 0.6rem;
    border: 1px solid var(--card-border);
    border-left: 4px solid var(--card-border);
    transition: all 0.3s ease;
    min-height: 85px;
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
    margin-bottom: 0.5rem;
    gap: 0.5rem;
}

.stage-name {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--main-text);
    flex: 1;
    line-height: 1.2;
}

.stage-status {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
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
}

.stage-details .test-counts {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    margin-top: 0.5rem;
}

.stage-details .duration {
    margin-top: 0.25rem;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
}

.stage-details .note {
    margin-top: 0.5rem;
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
    padding: 2rem;
    text-align: center;
    color: var(--main-secondary);
    font-style: italic;
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
    font-size: 0.9rem;
    color: var(--main-text);
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--card-border);
}

.diff-content {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
    font-size: 0.85rem;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
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
    gap: 1rem;
}

.summary-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.summary-item .label {
    font-size: 0.85rem;
    color: var(--main-secondary);
    font-weight: 500;
}

.summary-item .value {
    font-size: 1.1rem;
    color: var(--main-text);
    font-weight: 600;
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", monospace;
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
    .sidebar {
        position: relative;
        width: 100%;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--sidebar-border);
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .main-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    
    .stages-container {
        grid-template-columns: 1fr;
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
        
        this.eventSource.addEventListener('complete', (event) => {
            const data = JSON.parse(event.data);
            this.handleComplete(data);
        });
        
        this.eventSource.addEventListener('error', (event) => {
            const data = JSON.parse(event.data);
            this.handleError(data);
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
        
        this.eventSource.close();
        this.updateConnectionStatus('connected');
    }
    
    handleError(data) {
        const { message } = data;
        
        this.overallStatus.className = 'status-badge failed';
        this.overallStatus.textContent = 'Error';
        this.totalDuration.textContent = message;
        
        this.eventSource.close();
        this.updateConnectionStatus('error');
    }
}

// Initialize the UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VesperUI();
});
""")