"""
Custom Threaded HTTP Server Module.

Serves frontend files efficiently, forces correct MIME types,
and provides a dynamic API endpoint for network configuration.
"""

import http.server
import json
import mimetypes
import socket
import socketserver

PORT = 8000


def get_local_ip() -> str:
    """
    Determine the machine's local network IP address dynamically.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Does not send actual data, just evaluates the routing table
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


class SecureHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom request handler to serve static files and dynamic API routes.
    """

    def do_GET(self) -> None:
        """
        Intercept API requests for network configuration, otherwise serve static files.
        """
        if self.path == "/api/server-info":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.end_headers()

            response_data = {"server_ip": get_local_ip()}
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return

        super().do_GET()

    def end_headers(self) -> None:
        """Inject headers to prevent browser caching for static files."""
        if self.path != "/api/server-info":
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()


def start_server() -> None:
    """Initialize and start the threaded HTTP server."""
    mimetypes.init()
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")

    with socketserver.ThreadingTCPServer(("", PORT), SecureHTTPRequestHandler) as httpd:
        print(f"Web server active on http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Web server shutting down.")


if __name__ == "__main__":
    start_server()
