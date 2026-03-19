import unittest
from unittest.mock import patch, MagicMock
import requests

from notifiers.telegram import TelegramNotifier


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


if __name__ == "__main__":
    unittest.main()
