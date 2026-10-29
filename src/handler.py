"""Shared Command Handler for Data Broker Opt-Out Bot."""
import random
import string
import logging
from typing import Dict, Optional, Tuple
from src.models import Message, TransportType, UserAccount
from src.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class CommandHandler:
    """Processes incoming messages for both Telegram and WhatsApp using adapter pattern."""

    def __init__(self):
        # Accounts indexed by account user_id
        self.accounts: Dict[str, UserAccount] = {}
        # Mappings from platform-specific IDs to core account user_id
        self.telegram_map: Dict[str, str] = {}
        self.whatsapp_map: Dict[str, str] = {}
        # Active link tokens mapping token -> telegram_user_id
        self.link_tokens: Dict[str, str] = {}
        # Opt-out requests tracking user_id -> dict of broker: status
        self.optout_requests: Dict[str, Dict[str, str]] = {}

    def get_or_create_account(self, sender_id: str, transport: TransportType) -> UserAccount:
        """Retrieve existing account or create a new one for the given transport sender ID."""
        if transport == TransportType.TELEGRAM:
            if sender_id in self.telegram_map:
                user_id = self.telegram_map[sender_id]
                return self.accounts[user_id]
            user_id = f"user_tg_{sender_id}"
            account = UserAccount(user_id=user_id, telegram_id=sender_id)
            self.accounts[user_id] = account
            self.telegram_map[sender_id] = user_id
            return account

        elif transport == TransportType.WHATSAPP:
            if sender_id in self.whatsapp_map:
                user_id = self.whatsapp_map[sender_id]
                return self.accounts[user_id]
            user_id = f"user_wa_{sender_id}"
            account = UserAccount(user_id=user_id, whatsapp_id=sender_id, opted_in_whatsapp=False)
            self.accounts[user_id] = account
            self.whatsapp_map[sender_id] = user_id
            return account

        raise ValueError(f"Unsupported transport: {transport}")

    def generate_link_token(self, account: UserAccount) -> str:
        """Generate a 6-character link token for linking WhatsApp."""
        token = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        account.link_token = token
        if account.telegram_id:
            self.link_tokens[token] = account.telegram_id
        return token

    def link_accounts(self, token: str, whatsapp_id: str) -> Tuple[bool, str]:
        """Link WhatsApp ID to Telegram account using link token."""
        if token not in self.link_tokens:
            return False, "Invalid or expired link code. Please generate a new code using /link_whatsapp on Telegram."

        telegram_id = self.link_tokens.pop(token)
        tg_user_id = self.telegram_map.get(telegram_id)
        if not tg_user_id or tg_user_id not in self.accounts:
            return False, "Associated Telegram account not found."

        tg_account = self.accounts[tg_user_id]

        # Merge or update whatsapp ID
        tg_account.whatsapp_id = whatsapp_id
        tg_account.opted_in_whatsapp = True
        self.whatsapp_map[whatsapp_id] = tg_user_id

        return True, "Your WhatsApp account has been successfully linked to your Data Broker Opt-Out Bot account!"

    def handle_message(self, message: Message, adapter: BaseAdapter) -> Optional[str]:
        """Process incoming standardized message and send response via adapter."""
        text = message.text.strip()
        parts = text.split(maxsplit=1)
        command = parts[0].lower() if parts else ""
        args = parts[1].strip() if len(parts) > 1 else ""

        account = self.get_or_create_account(message.sender_id, message.transport)

        # WhatsApp Opt-In Verification
        if message.transport == TransportType.WHATSAPP:
            # Commands allowed before opt-in: /start, /help, /optin, /link_whatsapp
            allowed_pre_optin = ["/start", "/help", "/optin", "/link_whatsapp"]
            if not account.opted_in_whatsapp and command not in allowed_pre_optin:
                reply = (
                    "🔒 WhatsApp Opt-In Required.\n"
                    "To process opt-out requests via WhatsApp, please opt in by sending /optin, "
                    "or link your existing account by sending /link_whatsapp <code>."
                )
                adapter.send_message(message.sender_id, reply)
                return reply

        # Command Routing
        if command == "/start":
            reply = self._cmd_start(account, message.transport)
        elif command == "/help":
            reply = self._cmd_help(account, message.transport)
        elif command == "/optin":
            reply = self._cmd_optin(account, message.transport)
        elif command == "/link_whatsapp":
            reply = self._cmd_link_whatsapp(account, message.transport, args)
        elif command == "/optout":
            reply = self._cmd_optout(account, args)
        elif command == "/status":
            reply = self._cmd_status(account)
        else:
            reply = "Unknown command. Type /help to see the list of available commands."

        adapter.send_message(message.sender_id, reply)
        return reply

    def _cmd_start(self, account: UserAccount, transport: TransportType) -> str:
        msg = (
            "Welcome to Data Broker Opt-Out Bot!\n"
            "Protect your personal data by submitting automated opt-out requests to data brokers.\n\n"
            "Available commands:\n"
            "/optout <broker> - Submit opt-out request\n"
            "/status - View status of your requests\n"
            "/link_whatsapp - Link Telegram and WhatsApp accounts\n"
            "/optin - Opt in to WhatsApp messaging\n"
            "/help - Show command help"
        )
        if transport == TransportType.WHATSAPP and not account.opted_in_whatsapp:
            msg += "\n\nNote: Send /optin to enable opt-out requests on WhatsApp."
        return msg

    def _cmd_help(self, account: UserAccount, transport: TransportType) -> str:
        return (
            "🤖 Data Broker Opt-Out Bot Commands:\n"
            "• /optout <broker_name> - Request opt-out (e.g. /optout Serasa)\n"
            "• /status - Check pending and completed opt-out requests\n"
            "• /link_whatsapp - Generate link code on Telegram or send code on WhatsApp\n"
            "• /optin - Opt in to WhatsApp notifications and commands\n"
            "• /help - Display this help message"
        )

    def _cmd_optin(self, account: UserAccount, transport: TransportType) -> str:
        if transport == TransportType.WHATSAPP:
            account.opted_in_whatsapp = True
            return "✅ You have successfully opted in to Data Broker Opt-Out Bot on WhatsApp."
        return "You are using Telegram. Opt-in is already active on Telegram!"

    def _cmd_link_whatsapp(self, account: UserAccount, transport: TransportType, args: str) -> str:
        if transport == TransportType.TELEGRAM:
            token = self.generate_link_token(account)
            return (
                f"🔗 To link your WhatsApp account:\n"
                f"1. Open WhatsApp and send the following command:\n"
                f"   /link_whatsapp {token}\n"
                f"This code will link your WhatsApp number to your Telegram account ({account.telegram_id})."
            )
        elif transport == TransportType.WHATSAPP:
            if not args:
                return "Usage on WhatsApp: /link_whatsapp <code>\nGenerate code on Telegram first."
            success, msg = self.link_accounts(args, account.whatsapp_id or "")
            return msg
        return "Linking failed."

    def _cmd_optout(self, account: UserAccount, broker: str) -> str:
        if not broker:
            return "Please specify a broker name. Example: /optout Serasa"

        user_id = account.user_id
        if user_id not in self.optout_requests:
            self.optout_requests[user_id] = {}

        self.optout_requests[user_id][broker.lower()] = "IN_PROGRESS"
        return f"📩 Opt-out request submitted for broker '{broker}'. Use /status to check updates."

    def _cmd_status(self, account: UserAccount) -> str:
        user_id = account.user_id
        requests = self.optout_requests.get(user_id, {})
        if not requests:
            return "No active or completed opt-out requests found. Submit one with /optout <broker>."

        status_lines = [f"• {broker.capitalize()}: {status}" for broker, status in requests.items()]
        return "📊 Your Opt-Out Requests:\n" + "\n".join(status_lines)
