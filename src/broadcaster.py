import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Iterable, Optional, Set

try:
    from telegram import Bot
    from telegram.error import Forbidden, NetworkError, RetryAfter, TelegramError, TimedOut
except ImportError:
    # Fallback types for testing/mocking if telegram package isn't loaded
    class TelegramError(Exception):
        pass

    class RetryAfter(TelegramError):
        def __init__(self, retry_after: float):
            self.retry_after = retry_after
            super().__init__(f"Retry after {retry_after} seconds")

    class Forbidden(TelegramError):
        pass

    class NetworkError(TelegramError):
        pass

    class TimedOut(TelegramError):
        pass

    Bot = None

logger = logging.getLogger(__name__)


@dataclass
class BroadcastStats:
    total_users: int = 0
    success_count: int = 0
    failed_count: int = 0
    blocked_count: int = 0
    duration_seconds: float = 0.0
    rate_msg_per_sec: float = 0.0


class BroadcastService:
    def __init__(self, rate_limit: float = 30.0, max_retries: int = 3):
        """
        :param rate_limit: Maximum messages per second (default 30 msg/s).
        :param max_retries: Maximum number of retries per user for transient errors.
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries

    async def _send_message_with_retry(
        self, bot: Bot, user_id: int, text: str, parse_mode: Optional[str] = None
    ) -> str:
        """
        Sends a single message with retries on rate limits or network issues.
        Returns outcome: "success", "blocked", or "failed".
        """
        retries = 0
        backoff = 1.0

        while True:
            try:
                await bot.send_message(chat_id=user_id, text=text, parse_mode=parse_mode)
                return "success"
            except RetryAfter as e:
                retry_after = getattr(e, "retry_after", 1.0)
                logger.warning(
                    f"Rate limited (RetryAfter) for user {user_id}. Waiting {retry_after}s..."
                )
                await asyncio.sleep(retry_after)
            except Forbidden as e:
                logger.info(f"User {user_id} has blocked the bot or account deleted: {e}")
                return "blocked"
            except (NetworkError, TimedOut) as e:
                retries += 1
                if retries > self.max_retries:
                    logger.error(
                        f"Failed to send message to user {user_id} after {self.max_retries} retries: {e}"
                    )
                    return "failed"
                logger.warning(
                    f"Transient error sending to user {user_id} ({e}). Retrying in {backoff}s (attempt {retries}/{self.max_retries})..."
                )
                await asyncio.sleep(backoff)
                backoff *= 2.0
            except Exception as e:
                # Check duck-typing for RetryAfter if not direct subclass
                if hasattr(e, "retry_after"):
                    retry_after = getattr(e, "retry_after")
                    logger.warning(
                        f"Rate limited (duck-typed RetryAfter) for user {user_id}. Waiting {retry_after}s..."
                    )
                    await asyncio.sleep(retry_after)
                    continue
                logger.error(f"Unexpected error sending message to user {user_id}: {e}")
                return "failed"

    async def broadcast(
        self,
        bot: Bot,
        user_ids: Iterable[int],
        text: str,
        parse_mode: Optional[str] = None,
        user_storage: Optional[object] = None,
    ) -> BroadcastStats:
        """
        Broadcasts a message to all active users with rate limiting (30 msg/s target).
        """
        start_time = time.monotonic()
        user_list = list(user_ids)
        stats = BroadcastStats(total_users=len(user_list))

        interval = 1.0 / self.rate_limit if self.rate_limit > 0 else 0.0
        logger.info(
            f"Starting broadcast to {stats.total_users} users with max rate {self.rate_limit} msg/s"
        )

        for i, user_id in enumerate(user_list):
            msg_start = time.monotonic()
            outcome = await self._send_message_with_retry(bot, user_id, text, parse_mode=parse_mode)

            if outcome == "success":
                stats.success_count += 1
            elif outcome == "blocked":
                stats.blocked_count += 1
                if user_storage and hasattr(user_storage, "remove_user"):
                    user_storage.remove_user(user_id)
            else:
                stats.failed_count += 1

            # Rate limiting enforcement
            elapsed = time.monotonic() - msg_start
            sleep_time = interval - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        total_duration = time.monotonic() - start_time
        stats.duration_seconds = round(total_duration, 3)
        stats.rate_msg_per_sec = (
            round(stats.total_users / total_duration, 2) if total_duration > 0 else 0.0
        )

        logger.info(
            f"Broadcast completed: total={stats.total_users}, success={stats.success_count}, "
            f"failed={stats.failed_count}, blocked={stats.blocked_count}, "
            f"duration={stats.duration_seconds}s, rate={stats.rate_msg_per_sec} msg/s"
        )

        return stats
