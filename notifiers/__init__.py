from .base import Notifier
from .telegram import TelegramNotifier
from .discord import DiscordNotifier
from .email import EmailNotifier
import config


def get_notifier() -> Notifier:
    """Factory function to get the configured notifier."""
    notifier_type = config.NOTIFIER_TYPE

    if notifier_type == "telegram":
        return TelegramNotifier(
            bot_token=config.TELEGRAM_BOT_TOKEN,
            chat_id=config.TELEGRAM_CHAT_ID
        )
    elif notifier_type == "discord":
        return DiscordNotifier(webhook_url=config.DISCORD_WEBHOOK_URL)
    elif notifier_type == "email":
        return EmailNotifier(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            username=config.SMTP_USERNAME,
            password=config.SMTP_PASSWORD,
            from_email=config.EMAIL_FROM,
            to_emails=config.EMAIL_TO
        )
    else:
        raise ValueError(f"Unknown notifier type: {notifier_type}")