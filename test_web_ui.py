"""Test script to demonstrate the Vesper web UI in isolation."""
import time
from vesper.web_server import VesperWebServer, create_web_ui_files

def main():
    print("Starting Vesper Web UI test...")
    
    # Create web UI files
    web_ui_dir = "vesper/web_ui"
    create_web_ui_files(web_ui_dir)
    
    # Start web server
    web_server = VesperWebServer(port=8082, web_root=web_ui_dir)
    server_url = web_server.start()
    
    print(f"Web UI started at {server_url}")
    print("Simulating workflow stages...")
    
    # Simulate workflow stages
    stages = [
        ("baseline", "running", {}),
        ("baseline", "passed", {"counts": {"tests": 12, "failures": 0, "errors": 0, "skipped": 0}, "duration_seconds": 2.1}),
        ("seed", "running", {}),
        ("seed", "ok", {"note": "Swapped in seeded Checkout.java"}),
        ("reproduce", "running", {}),
        ("reproduce", "reproduced", {"counts": {"tests": 1, "failures": 1, "errors": 0, "skipped": 0}, "duration_seconds": 1.2, "note": "EXPECTED failure on seeded code — confirms defect is present"}),
        ("regress_bug", "running", {}),
        ("regress_bug", "failed", {"counts": {"tests": 12, "failures": 5, "errors": 0, "skipped": 0}, "duration_seconds": 1.2, "note": "Full regression on seeded code — failures expected from R3 boundary bug"}),
        ("restore", "running", {}),
        ("restore", "ok", {"note": "Restored fixed Checkout.java"}),
        ("verify", "running", {}),
        ("verify", "verified", {"counts": {"tests": 1, "failures": 0, "errors": 0, "skipped": 0}, "duration_seconds": 1.2}),
        ("regress_fix", "running", {}),
        ("regress_fix", "all_passed", {"counts": {"tests": 12, "failures": 0, "errors": 0, "skipped": 0}, "duration_seconds": 1.2}),
        ("report", "running", {}),
        ("report", "written", {"note": "Workflow report generated"}),
    ]
    
    for stage_name, status, data in stages:
        time.sleep(0.5)  # Simulate stage duration
        web_server.broadcast_stage(stage_name, status, data)
        print(f"  {stage_name}: {status}")
    
    # Complete workflow
    time.sleep(0.5)
    web_server.broadcast_complete("ok", 7.5)
    print("Workflow complete!")
    
    # Keep server running for viewing
    print(f"\nWeb UI will remain available at {server_url} for 15 seconds...")
    print("Open the URL in your browser to see the real-time updates.")
    time.sleep(15)
    
    web_server.stop()
    print("Web server stopped.")

if __name__ == "__main__":
    main()