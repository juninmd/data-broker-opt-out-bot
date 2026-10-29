"""
Telegram bot handler for the /lgpd_report command.
Generates and sends an official LGPD Art. 18 PDF report to the user.
"""
import os
import tempfile
import logging
from typing import Any, Callable, Dict, Optional
from .report_generator import generate_lgpd_report

logger = logging.getLogger(__name__)


def fetch_user_data_default(user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
    """
    Default mock/fallback user data provider.
    In production, this queries the bot database/repository.
    """
    return {
        "user_id": user_id,
        "name": username or f"Usuario_{user_id}",
        "email": "N/A",
        "cpf": "N/A",
        "requests": []
    }


async def handle_lgpd_report_command(
    update: Any,
    context: Any,
    data_fetcher: Optional[Callable[[int, Optional[str]], Dict[str, Any]]] = None
) -> Optional[str]:
    """
    Async Telegram command handler for /lgpd_report.

    :param update: telegram.Update object
    :param context: telegram.ext.ContextTypes.DEFAULT_TYPE object
    :param data_fetcher: Optional function(user_id, username) returning user data dict
    :return: Path to generated PDF file or None
    """
    fetcher = data_fetcher or fetch_user_data_default

    effective_user = getattr(update, "effective_user", None)
    user_id = getattr(effective_user, "id", 0) if effective_user else 0
    username = getattr(effective_user, "username", None) if effective_user else None

    # Inform user processing started
    message = getattr(update, "message", None)
    if message and hasattr(message, "reply_text"):
        await message.reply_text("Gerando seu relatorio LGPD (Art. 18)... Por favor, aguarde.")

    user_data = fetcher(user_id, username)

    temp_dir = tempfile.mkdtemp()
    pdf_filename = f"Relatorio_LGPD_User_{user_id}.pdf"
    pdf_path = os.path.join(temp_dir, pdf_filename)

    try:
        generate_lgpd_report(user_data, pdf_path)

        if message and hasattr(message, "reply_document"):
            with open(pdf_path, "rb") as doc_file:
                await message.reply_document(
                    document=doc_file,
                    filename=pdf_filename,
                    caption="Aqui esta o seu Relatorio de Direitos do Titular de Dados (Art. 18 da LGPD)."
                )
        return pdf_path
    except Exception as exc:
        logger.error("Error generating LGPD report for user %s: %s", user_id, exc)
        if message and hasattr(message, "reply_text"):
            await message.reply_text("Ocorreu um erro ao gerar seu relatorio LGPD. Tente novamente mais tarde.")
        raise exc
