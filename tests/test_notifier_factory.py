import unittest
from unittest.mock import patch

import notifiers
from notifiers.discord import DiscordNotifier
from notifiers.email import EmailNotifier
from notifiers.telegram import TelegramNotifier


class NotifierFactoryTest(unittest.TestCase):
    @patch("config.NOTIFIER_TYPE", "telegram")
    @patch("config.TELEGRAM_BOT_TOKEN", "bot-token")
    @patch("config.TELEGRAM_CHAT_ID", "chat-id")
    def test_get_telegram_notifier(self):
        notifier = notifiers.get_notifier()
        self.assertIsInstance(notifier, TelegramNotifier)
        self.assertEqual(notifier.bot_token, "bot-token")
        self.assertEqual(notifier.chat_id, "chat-id")

    @patch("config.NOTIFIER_TYPE", "discord")
    @patch("config.DISCORD_WEBHOOK_URL", "https://discord.example/webhook")
    def test_get_discord_notifier(self):
        notifier = notifiers.get_notifier()
        self.assertIsInstance(notifier, DiscordNotifier)
        self.assertEqual(notifier.webhook_url, "https://discord.example/webhook")

    @patch("config.NOTIFIER_TYPE", "email")
    @patch("config.SMTP_HOST", "smtp.example.com")
    @patch("config.SMTP_PORT", 587)
    @patch("config.SMTP_USERNAME", "user@example.com")
    @patch("config.SMTP_PASSWORD", "secret")
    @patch("config.EMAIL_FROM", "user@example.com")
    @patch("config.EMAIL_TO", ["league@example.com"])
    def test_get_email_notifier(self):
        notifier = notifiers.get_notifier()
        self.assertIsInstance(notifier, EmailNotifier)
        self.assertEqual(notifier.smtp_host, "smtp.example.com")
        self.assertEqual(notifier.smtp_port, 587)
        self.assertEqual(notifier.to_emails, ["league@example.com"])

    @patch("config.NOTIFIER_TYPE", "myspace")
    def test_unknown_notifier_type_raises(self):
        with self.assertRaises(ValueError):
            notifiers.get_notifier()


if __name__ == "__main__":
    unittest.main()
