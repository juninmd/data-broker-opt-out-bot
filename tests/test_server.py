"""Integration tests for Webhook Gateway HTTP Server."""
import unittest
import threading
import json
import urllib.request
import urllib.parse
import hmac
import hashlib
from src.server import create_server


class TestWebhookGatewayServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Bind to port 0 for random free port
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{cls.port}"

        # Configure test verify_token and app_secret on server's whatsapp_adapter
        cls.server.RequestHandlerClass.whatsapp_adapter.verify_token = "my_secret_verify_token"
        cls.server.RequestHandlerClass.whatsapp_adapter.app_secret = "my_app_secret_123"

        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_check(self):
        req = urllib.request.Request(f"{self.base_url}/health")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "ok")
            self.assertIn("whatsapp", data["transports"])

    def test_whatsapp_webhook_verification_get(self):
        # Valid challenge request from Meta
        params = urllib.parse.urlencode({
            "hub.mode": "subscribe",
            "hub.verify_token": "my_secret_verify_token",
            "hub.challenge": "115820123"
        })
        url = f"{self.base_url}/webhook/whatsapp?{params}"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read().decode("utf-8")
            self.assertEqual(body, "115820123")

        # Invalid token -> 403
        bad_params = urllib.parse.urlencode({
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "115820123"
        })
        bad_url = f"{self.base_url}/webhook/whatsapp?{bad_params}"
        try:
            urllib.request.urlopen(bad_url)
            self.fail("Expected HTTPError 403")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 403)

    def test_whatsapp_webhook_post_with_hmac_signature(self):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {"phone_number_id": "10001"},
                                "messages": [
                                    {
                                        "from": "5511955554444",
                                        "id": "wamid.999",
                                        "timestamp": "1672531199",
                                        "text": {"body": "/help"},
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        signature = hmac.new(b"my_app_secret_123", body_bytes, hashlib.sha256).hexdigest()

        # Test POST with valid signature
        req = urllib.request.Request(
            f"{self.base_url}/webhook/whatsapp",
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": f"sha256={signature}"
            },
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "success")

        # Test POST with invalid signature -> 401
        invalid_req = urllib.request.Request(
            f"{self.base_url}/webhook/whatsapp",
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": "sha256=invalid_signature"
            },
            method="POST"
        )
        try:
            urllib.request.urlopen(invalid_req)
            self.fail("Expected HTTPError 401")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)


if __name__ == "__main__":
    unittest.main()
