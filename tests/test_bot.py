from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot import BotApp
from src.config import Config
from src.storage import UserStorage


@pytest.fixture
def mock_config():
    config = Config()
    config.admin_ids = {1001}
    return config


@pytest.fixture
def mock_storage():
    storage = UserStorage()
    storage.add_user(2001)
    storage.add_user(2002)
    return storage


@pytest.mark.asyncio
async def test_broadcast_unauthorized(mock_config, mock_storage):
    app = BotApp(config=mock_config, storage=mock_storage)

    update = MagicMock()
    update.effective_user.id = 9999  # Not an admin
    update.message.reply_text = AsyncMock()

    context = MagicMock()

    await app.broadcast_handler(update, context)

    update.message.reply_text.assert_called_once_with("⛔ Unauthorized: Admin access required.")


@pytest.mark.asyncio
async def test_broadcast_no_text_provided(mock_config, mock_storage):
    app = BotApp(config=mock_config, storage=mock_storage)

    update = MagicMock()
    update.effective_user.id = 1001  # Admin
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.args = []

    await app.broadcast_handler(update, context)

    assert update.message.reply_text.call_count == 1
    args, _ = update.message.reply_text.call_args
    assert "Usage:" in args[0]


@pytest.mark.asyncio
async def test_broadcast_success_as_admin(mock_config, mock_storage):
    broadcaster = AsyncMock()
    mock_stats = MagicMock()
    mock_stats.total_users = 2
    mock_stats.success_count = 2
    mock_stats.failed_count = 0
    mock_stats.blocked_count = 0
    mock_stats.duration_seconds = 0.1
    mock_stats.rate_msg_per_sec = 20.0
    broadcaster.broadcast = AsyncMock(return_value=mock_stats)

    app = BotApp(config=mock_config, storage=mock_storage, broadcaster=broadcaster)

    status_msg = MagicMock()
    status_msg.edit_text = AsyncMock()

    update = MagicMock()
    update.effective_user.id = 1001  # Admin
    update.message.reply_to_message = None
    update.message.reply_text = AsyncMock(return_value=status_msg)

    context = MagicMock()
    context.args = ["Announcement", "test"]

    await app.broadcast_handler(update, context)

    broadcaster.broadcast.assert_called_once()
    assert status_msg.edit_text.call_count == 1
    report_text = status_msg.edit_text.call_args[0][0]
    assert "Broadcast completed" in report_text
    assert "Successful: 2" in report_text
