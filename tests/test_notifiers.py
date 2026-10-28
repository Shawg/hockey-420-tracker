import unittest
from unittest.mock import patch, MagicMock
import requests

from notifiers.telegram import TelegramNotifier
from notifiers.discord import DiscordNotifier
from notifiers.email import EmailNotifier


class TelegramNotifierTest(unittest.TestCase):
    def test_send_missing_token(self):
        notifier = TelegramNotifier("", "chat123")
        result = notifier.send("test message")
        self.assertFalse(result)

    def test_send_missing_chat_id(self):
        notifier = TelegramNotifier("token123", "")
        result = notifier.send("test message")
        self.assertFalse(result)

    def test_send_missing_both(self):
        notifier = TelegramNotifier("", "")
        result = notifier.send("test message")
        self.assertFalse(result)

    @patch('notifiers.telegram.requests.post')
    def test_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        notifier = TelegramNotifier("test_token", "test_chat_id")
        result = notifier.send("Test message")

        self.assertTrue(result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn("sendMessage", call_args[0][0])
        self.assertEqual(call_args[1]["json"]["chat_id"], "test_chat_id")
        self.assertEqual(call_args[1]["json"]["text"], "Test message")
        self.assertEqual(call_args[1]["json"]["parse_mode"], "Markdown")

    @patch('notifiers.telegram.requests.post')
    def test_send_api_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("API error")

        notifier = TelegramNotifier("test_token", "test_chat_id")
        result = notifier.send("Test message")

        self.assertFalse(result)

    @patch('notifiers.telegram.requests.post')
    def test_send_empty_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        notifier = TelegramNotifier("test_token", "test_chat_id")
        result = notifier.send("")

        self.assertTrue(result)
        mock_post.assert_called_once()


class DiscordNotifierTest(unittest.TestCase):
    @patch('notifiers.discord.requests.post')
    def test_send_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        notifier = DiscordNotifier("https://discord.example/webhook")
        result = notifier.send("Test message")

        self.assertTrue(result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://discord.example/webhook")
        self.assertEqual(call_args[1]["json"]["content"], "Test message")
        self.assertEqual(call_args[1]["timeout"], 10)

    def test_send_missing_webhook(self):
        notifier = DiscordNotifier("")
        self.assertFalse(notifier.send("Test message"))

    @patch('notifiers.discord.requests.post')
    def test_send_api_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("API error")

        notifier = DiscordNotifier("https://discord.example/webhook")
        result = notifier.send("Test message")

        self.assertFalse(result)

    @patch('notifiers.discord.requests.post')
    def test_send_http_error_status(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        mock_post.return_value = mock_response

        notifier = DiscordNotifier("https://discord.example/webhook")
        self.assertFalse(notifier.send("Test message"))


class EmailNotifierTest(unittest.TestCase):
    def make_notifier(self, **overrides):
        settings = {
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "username": "user@example.com",
            "password": "secret",
            "from_email": "user@example.com",
            "to_emails": ["league@example.com"],
        }
        settings.update(overrides)
        return EmailNotifier(**settings)

    def test_send_missing_config(self):
        notifier = self.make_notifier(smtp_host="")
        self.assertFalse(notifier.send("Test message"))

    def test_send_missing_recipients(self):
        notifier = self.make_notifier(to_emails=[])
        self.assertFalse(notifier.send("Test message"))

    @patch('notifiers.email.smtplib.SMTP')
    def test_send_success(self, mock_smtp):
        server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = server

        notifier = self.make_notifier()
        result = notifier.send("Test message")

        self.assertTrue(result)
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("user@example.com", "secret")
        server.send_message.assert_called_once()

        sent_msg = server.send_message.call_args[0][0]
        self.assertEqual(sent_msg["From"], "user@example.com")
        self.assertEqual(sent_msg["To"], "league@example.com")
        self.assertEqual(sent_msg["Subject"], "4:20 Goal Alert!")

    @patch('notifiers.email.smtplib.SMTP')
    def test_send_smtp_failure(self, mock_smtp):
        mock_smtp.side_effect = OSError("Connection refused")

        notifier = self.make_notifier()
        self.assertFalse(notifier.send("Test message"))

    @patch('notifiers.email.smtplib.SMTP')
    def test_send_login_failure(self, mock_smtp):
        server = MagicMock()
        server.login.side_effect = Exception("Authentication failed")
        mock_smtp.return_value.__enter__.return_value = server

        notifier = self.make_notifier()
        self.assertFalse(notifier.send("Test message"))


if __name__ == "__main__":
    unittest.main()
