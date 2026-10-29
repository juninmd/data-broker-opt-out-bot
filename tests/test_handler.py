"""Unit tests for CommandHandler logic and account linking."""
import unittest
from src.handler import CommandHandler
from src.adapters.telegram import TelegramAdapter
from src.adapters.whatsapp import WhatsAppAdapter
from src.models import Message, TransportType


class TestCommandHandler(unittest.TestCase):

    def setUp(self):
        self.handler = CommandHandler()
        self.tg_adapter = TelegramAdapter()
        self.wa_adapter = WhatsAppAdapter()

    def test_identical_commands_on_both_transports(self):
        # 1. /start command
        msg_tg = Message("1001", "1001", TransportType.TELEGRAM, "/start")
        reply_tg = self.handler.handle_message(msg_tg, self.tg_adapter)
        self.assertIn("Welcome to Data Broker Opt-Out Bot", reply_tg)

        msg_wa = Message("5511990001111", "10001", TransportType.WHATSAPP, "/start")
        reply_wa = self.handler.handle_message(msg_wa, self.wa_adapter)
        self.assertIn("Welcome to Data Broker Opt-Out Bot", reply_wa)

        # 2. /help command
        msg_tg_help = Message("1001", "1001", TransportType.TELEGRAM, "/help")
        reply_tg_help = self.handler.handle_message(msg_tg_help, self.tg_adapter)
        self.assertIn("Data Broker Opt-Out Bot Commands", reply_tg_help)

        msg_wa_help = Message("5511990001111", "10001", TransportType.WHATSAPP, "/help")
        reply_wa_help = self.handler.handle_message(msg_wa_help, self.wa_adapter)
        self.assertIn("Data Broker Opt-Out Bot Commands", reply_wa_help)

    def test_whatsapp_optin_enforcement(self):
        wa_sender = "5511988887777"

        # Un-opted-in WhatsApp user attempts /optout
        msg_optout = Message(wa_sender, "10001", TransportType.WHATSAPP, "/optout Serasa")
        reply = self.handler.handle_message(msg_optout, self.wa_adapter)
        self.assertIn("WhatsApp Opt-In Required", reply)

        # Send /optin
        msg_optin = Message(wa_sender, "10001", TransportType.WHATSAPP, "/optin")
        reply_optin = self.handler.handle_message(msg_optin, self.wa_adapter)
        self.assertIn("successfully opted in", reply_optin)

        # Now /optout works
        reply_optout_after = self.handler.handle_message(msg_optout, self.wa_adapter)
        self.assertIn("Opt-out request submitted for broker 'Serasa'", reply_optout_after)

    def test_account_linking_flow(self):
        tg_user_id = "2002"
        wa_user_id = "5511977776666"

        # 1. Telegram user requests /link_whatsapp
        msg_tg = Message(tg_user_id, tg_user_id, TransportType.TELEGRAM, "/link_whatsapp")
        reply_tg = self.handler.handle_message(msg_tg, self.tg_adapter)
        self.assertIn("/link_whatsapp ", reply_tg)

        # Extract code from response
        # Token is after "/link_whatsapp "
        token_line = [line for line in reply_tg.split("\n") if "/link_whatsapp " in line][0]
        token = token_line.split("/link_whatsapp ")[1].strip()

        # 2. WhatsApp user sends /link_whatsapp <code>
        msg_wa = Message(wa_user_id, "10001", TransportType.WHATSAPP, f"/link_whatsapp {token}")
        reply_wa = self.handler.handle_message(msg_wa, self.wa_adapter)
        self.assertIn("successfully linked", reply_wa)

        # 3. Verify WhatsApp account is now opted in and shares the same state / account as Telegram user
        account_wa = self.handler.get_or_create_account(wa_user_id, TransportType.WHATSAPP)
        self.assertTrue(account_wa.opted_in_whatsapp)
        self.assertEqual(account_wa.telegram_id, tg_user_id)

        # Submitting opt-out on Telegram shows in status on WhatsApp
        self.handler.handle_message(Message(tg_user_id, tg_user_id, TransportType.TELEGRAM, "/optout Experian"), self.tg_adapter)

        reply_wa_status = self.handler.handle_message(Message(wa_user_id, "10001", TransportType.WHATSAPP, "/status"), self.wa_adapter)
        self.assertIn("Experian: IN_PROGRESS", reply_wa_status)


if __name__ == "__main__":
    unittest.main()
