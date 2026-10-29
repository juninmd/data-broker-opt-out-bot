import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram.error import Forbidden, NetworkError, RetryAfter

from src.broadcaster import BroadcastService, BroadcastStats
from src.storage import UserStorage


@pytest.mark.asyncio
async def test_broadcast_success_and_rate_limiting():
    service = BroadcastService(rate_limit=50.0, max_retries=1)
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=True)

    user_ids = list(range(1001, 1011))  # 10 users

    start = time.monotonic()
    stats = await service.broadcast(bot=bot, user_ids=user_ids, text="Hello world")
    elapsed = time.monotonic() - start

    assert stats.total_users == 10
    assert stats.success_count == 10
    assert stats.failed_count == 0
    assert stats.blocked_count == 0
    assert bot.send_message.call_count == 10
    # At 50 msg/s, 10 messages take at least ~0.18s
    assert elapsed >= 0.15


@pytest.mark.asyncio
async def test_broadcast_retry_after():
    service = BroadcastService(rate_limit=100.0, max_retries=2)
    bot = AsyncMock()

    call_count = 0

    async def mock_send_message(chat_id, text, parse_mode=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RetryAfter(retry_after=0.01)
        return True

    bot.send_message = AsyncMock(side_effect=mock_send_message)

    stats = await service.broadcast(bot=bot, user_ids=[101], text="Retry test")

    assert stats.success_count == 1
    assert call_count == 2


@pytest.mark.asyncio
async def test_broadcast_forbidden_blocked_removes_user():
    service = BroadcastService(rate_limit=100.0, max_retries=1)
    bot = AsyncMock()
    bot.send_message = AsyncMock(side_effect=Forbidden("Bot was blocked by the user"))

    storage = UserStorage()
    storage.add_user(201)
    storage.add_user(202)

    stats = await service.broadcast(
        bot=bot, user_ids=[201], text="Test blocked", user_storage=storage
    )

    assert stats.blocked_count == 1
    assert stats.success_count == 0
    assert 201 not in storage.get_active_users()
    assert 202 in storage.get_active_users()


@pytest.mark.asyncio
async def test_broadcast_network_error_retry_and_failure():
    service = BroadcastService(rate_limit=100.0, max_retries=2)
    bot = AsyncMock()
    bot.send_message = AsyncMock(side_effect=NetworkError("Connection reset"))

    stats = await service.broadcast(bot=bot, user_ids=[301], text="Test network fail")

    assert stats.failed_count == 1
    assert stats.success_count == 0
    # Initial attempt + 2 retries = 3 calls
    assert bot.send_message.call_count == 3
