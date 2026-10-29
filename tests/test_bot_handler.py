"""
Unit tests for LGPD Telegram bot command handler.
"""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.lgpd.bot_handler import handle_lgpd_report_command, fetch_user_data_default


@pytest.mark.asyncio
async def test_handle_lgpd_report_command():
    mock_message = AsyncMock()
    mock_message.reply_text = AsyncMock()
    mock_message.reply_document = AsyncMock()

    mock_user = MagicMock()
    mock_user.id = 555444
    mock_user.username = "teste_user"

    mock_update = MagicMock()
    mock_update.effective_user = mock_user
    mock_update.message = mock_message

    mock_context = MagicMock()

    def custom_fetcher(user_id, username):
        return {
            "user_id": user_id,
            "name": username,
            "email": "user@test.com",
            "cpf": "***.000.111-**",
            "requests": [
                {"broker": "DataBrokerX", "date": "10/10/2026", "status": "Concluido", "protocol": "PROT123"}
            ]
        }

    pdf_path = await handle_lgpd_report_command(mock_update, mock_context, data_fetcher=custom_fetcher)

    assert pdf_path is not None
    assert os.path.exists(pdf_path)
    assert mock_message.reply_text.called
    assert mock_message.reply_document.called

    # Clean up
    if os.path.exists(pdf_path):
        os.remove(pdf_path)


def test_fetch_user_data_default():
    data = fetch_user_data_default(12345, "john_doe")
    assert data["user_id"] == 12345
    assert data["name"] == "john_doe"
    assert data["requests"] == []
