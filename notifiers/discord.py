from .base import Notifier

import logging
import requests

logger = logging.getLogger(__name__)


class DiscordNotifier(Notifier):
    """Discord webhook notification implementation."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, message: str) -> bool:
        if not self.webhook_url:
            logger.error("Discord webhook URL not configured")
            return False

        try:
            response = requests.post(
                self.webhook_url,
                json={"content": message},
                timeout=10
            )
            response.raise_for_status()
            logger.info("Discord notification sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False