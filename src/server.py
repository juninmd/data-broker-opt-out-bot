"""HTTP Webhook Gateway Server for Telegram and WhatsApp Transports."""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import logging
from typing import Optional
from src.adapters.telegram import TelegramAdapter
from src.adapters.whatsapp import WhatsAppAdapter
from src.handler import CommandHandler

logger = logging.getLogger(__name__)


class WebhookGatewayHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Gateway Webhooks."""

    # Class-level shared instances
    command_handler: CommandHandler = CommandHandler()
    telegram_adapter: TelegramAdapter = TelegramAdapter()
    whatsapp_adapter: WhatsAppAdapter = WhatsAppAdapter()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/health":
            self._send_json(200, {
                "status": "ok",
                "transports": ["telegram", "whatsapp"]
            })
            return

        if path == "/webhook/whatsapp":
            mode = query_params.get("hub.mode", [None])[0]
            token = query_params.get("hub.verify_token", [None])[0]
            challenge = query_params.get("hub.challenge", [None])[0]

            res_challenge = self.whatsapp_adapter.verify_challenge(mode, token, challenge)
            if res_challenge:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(res_challenge.encode("utf-8"))
            else:
                self._send_json(403, {"error": "Webhook verification failed"})
            return

        self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        headers_dict = {k: v for k, v in self.headers.items()}

        if path == "/webhook/whatsapp":
            if not self.whatsapp_adapter.verify_webhook(headers_dict, body):
                self._send_json(401, {"error": "Invalid X-Hub-Signature-256 signature"})
                return

            try:
                payload = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                self._send_json(400, {"error": "Invalid JSON"})
                return

            msg = self.whatsapp_adapter.parse_incoming(payload)
            if msg:
                self.command_handler.handle_message(msg, self.whatsapp_adapter)

            self._send_json(200, {"status": "success"})
            return

        elif path == "/webhook/telegram":
            try:
                payload = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                self._send_json(400, {"error": "Invalid JSON"})
                return

            msg = self.telegram_adapter.parse_incoming(payload)
            if msg:
                self.command_handler.handle_message(msg, self.telegram_adapter)

            self._send_json(200, {"status": "success"})
            return

        self._send_json(404, {"error": "Not Found"})

    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        # Override to suppress default HTTP server log spamming in tests
        pass


def create_server(host: str = "0.0.0.0", port: int = 8080) -> HTTPServer:
    """Create and return configured gateway HTTPServer."""
    return HTTPServer((host, port), WebhookGatewayHandler)


if __name__ == "__main__":
    server = create_server("0.0.0.0", 8080)
    print("Starting WhatsApp & Telegram API Gateway on port 8080...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
