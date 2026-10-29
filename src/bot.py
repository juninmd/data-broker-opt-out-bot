import logging
from typing import Optional

from src.broadcaster import BroadcastService, BroadcastStats
from src.config import Config
from src.storage import UserStorage

logger = logging.getLogger(__name__)


class BotApp:
    def __init__(self, config: Config, storage: UserStorage, broadcaster: Optional[BroadcastService] = None):
        self.config = config
        self.storage = storage
        self.broadcaster = broadcaster or BroadcastService()

    async def broadcast_handler(self, update, context) -> None:
        """
        /broadcast [message] - Admin-only broadcast command.
        Can also be used in reply to a message to broadcast the replied message text.
        """
        user = update.effective_user
        if not user or not self.config.is_admin(user.id):
            logger.warning(f"Unauthorized broadcast attempt by user {user.id if user else 'Unknown'}")
            if update.message:
                await update.message.reply_text("⛔ Unauthorized: Admin access required.")
            return

        # Determine text to broadcast
        text_to_send = ""
        if update.message.reply_to_message and update.message.reply_to_message.text:
            text_to_send = update.message.reply_to_message.text
        elif context.args:
            text_to_send = " ".join(context.args)

        if not text_to_send:
            await update.message.reply_text(
                "Usage:\n`/broadcast <message>` or reply to a message with `/broadcast`.",
                parse_mode="Markdown",
            )
            return

        active_users = self.storage.get_active_users()
        if not active_users:
            await update.message.reply_text("No active users found to broadcast to.")
            return

        status_msg = await update.message.reply_text(
            f"📢 Starting broadcast to {len(active_users)} active users..."
        )

        stats: BroadcastStats = await self.broadcaster.broadcast(
            bot=context.bot,
            user_ids=active_users,
            text=text_to_send,
            user_storage=self.storage,
        )

        report = (
            f"✅ *Broadcast completed*\n\n"
            f"👥 Total Target: {stats.total_users}\n"
            f"🟢 Successful: {stats.success_count}\n"
            f"🔴 Failed: {stats.failed_count}\n"
            f"🚫 Blocked/Removed: {stats.blocked_count}\n"
            f"⏱️ Duration: {stats.duration_seconds}s\n"
            f"⚡ Rate: {stats.rate_msg_per_sec} msg/s"
        )

        if status_msg:
            await status_msg.edit_text(report, parse_mode="Markdown")
        else:
            await update.message.reply_text(report, parse_mode="Markdown")
