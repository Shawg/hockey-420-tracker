import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import main
import nhl_client


class MainIntegrationTest(unittest.TestCase):
    def test_main_runs_without_error(self):
        # run the main function; it will fetch yesterday's games and
        # send a notification (config must be set, else notifier may fail).
        # We just ensure it completes without raising.
        try:
            main.main()
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_with_specific_date(self):
        # monkey patch get_yesterday to use a fixed date
        original = main.get_yesterday
        target = datetime.now() - timedelta(days=1)
        main.get_yesterday = lambda: target
        try:
            main.main()
        finally:
            main.get_yesterday = original

    @patch('main.notifiers.get_notifier')
    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_no_notification_when_no_games(self, mock_get_games, mock_get_notifier):
        mock_get_games.return_value = []
        mock_notifier_instance = MagicMock()
        mock_get_notifier.return_value = mock_notifier_instance

        main.main()

        mock_notifier_instance.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
