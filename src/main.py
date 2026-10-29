import http.server
import socketserver
import os
import sys

PORT = int(os.getenv("PORT", "8000"))

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/health", "/"]:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"data-broker-opt-out-bot"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run():
    print(f"Starting Data Broker Opt-Out Bot service on port {PORT}...")
    with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run()
