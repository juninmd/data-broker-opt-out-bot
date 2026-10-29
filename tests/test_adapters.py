"""Unit tests for Telegram and WhatsApp adapters."""
import unittest
import hmac
import hashlib
from src.adapters.telegram import TelegramAdapter
from src.adapters.whatsapp import WhatsAppAdapter
from src.models import TransportType, Message


class TestTelegramAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = TelegramAdapter(bot_token="test_token", mock_mode=True)

    def test_transport_type(self):
        self.assertEqual(self.adapter.transport_type, TransportType.TELEGRAM)

    def test_parse_incoming_valid(self):
        payload = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "from": {"id": 98765, "is_bot": False, "first_name": "Alice"},
                "chat": {"id": 98765, "type": "private"},
                "date": 1672531199,
                "text": "/optout Serasa"
            }
        }
        msg = self.adapter.parse_incoming(payload)
        self.assertIsNotNone(msg)
        self.assertEqual(msg.sender_id, "98765")
        self.assertEqual(msg.recipient_id, "98765")
        self.assertEqual(msg.transport, TransportType.TELEGRAM)
        self.assertEqual(msg.text, "/optout Serasa")

    def test_parse_incoming_invalid(self):
        self.assertIsNone(self.adapter.parse_incoming({}))
        self.assertIsNone(self.adapter.parse_incoming({"message": {}}))

    def test_format_outgoing(self):
        formatted = self.adapter.format_outgoing("98765", "Hello")
        self.assertEqual(formatted, {
            "chat_id": "98765",
            "text": "Hello",
            "parse_mode": "HTML"
        })

    def test_send_message_mock(self):
        res = self.adapter.send_message("98765", "Hello")
        self.assertTrue(res)
        self.assertEqual(len(self.adapter.sent_messages), 1)


class TestWhatsAppAdapter(unittest.TestCase):

    def setUp(self):
        self.adapter = WhatsAppAdapter(
            phone_number_id="10001",
            access_token="MOCK_ACCESS_TOKEN",
            verify_token="test_verify_token",
            app_secret="test_secret_key",
            mock_mode=True
        )

    def test_transport_type(self):
        self.assertEqual(self.adapter.transport_type, TransportType.WHATSAPP)

    def test_parse_incoming_valid(self):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15550001",
                                    "phone_number_id": "10001"
                                },
                                "messages": [
                                    {
                                        "from": "5511999998888",
                                        "id": "wamid.123",
                                        "timestamp": "1672531199",
                                        "text": {"body": "/status"},
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
        msg = self.adapter.parse_incoming(payload)
        self.assertIsNotNone(msg)
        self.assertEqual(msg.sender_id, "5511999998888")
        self.assertEqual(msg.recipient_id, "10001")
        self.assertEqual(msg.transport, TransportType.WHATSAPP)
        self.assertEqual(msg.text, "/status")

    def test_verify_challenge(self):
        res = self.adapter.verify_challenge("subscribe", "test_verify_token", "challenge_code_123")
        self.assertEqual(res, "challenge_code_123")

        # Invalid token
        res_invalid = self.adapter.verify_challenge("subscribe", "wrong_token", "challenge_code_123")
        self.assertIsNone(res_invalid)

    def test_verify_webhook_signature(self):
        body = b'{"test": "payload"}'
        expected_hash = hmac.new(b"test_secret_key", body, hashlib.sha256).hexdigest()
        valid_header = {"X-Hub-Signature-256": f"sha256={expected_hash}"}

        self.assertTrue(self.adapter.verify_webhook(valid_header, body))

        invalid_header = {"X-Hub-Signature-256": "sha256=wrong_hash"}
        self.assertFalse(self.adapter.verify_webhook(invalid_header, body))

    def test_format_outgoing(self):
        formatted = self.adapter.format_outgoing("5511999998888", "Opt-out status: OK")
        self.assertEqual(formatted, {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "5511999998888",
            "type": "text",
            "text": {
                "body": "Opt-out status: OK"
            }
        })


if __name__ == "__main__":
    unittest.main()
