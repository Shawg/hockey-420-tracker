import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import main
import nhl_client


class HelperFunctionTest(unittest.TestCase):
    def test_is_monday_true(self):
        monday = datetime(2026, 3, 16, 10, 0, 0)  # March 16, 2026 is Monday
        with patch('main.datetime') as mock_datetime:
            mock_datetime.now.return_value = monday
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            self.assertTrue(main.is_monday())

    def test_is_monday_false(self):
        tuesday = datetime(2026, 3, 17, 10, 0, 0)  # March 17, 2026 is Tuesday
        with patch('main.datetime') as mock_datetime:
            mock_datetime.now.return_value = tuesday
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            self.assertFalse(main.is_monday())

    def test_get_week_date_range(self):
        monday = datetime(2026, 3, 16, 10, 0, 0)
        with patch('main.datetime') as mock_datetime:
            mock_datetime.now.return_value = monday
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            start, end = main.get_week_date_range()
            self.assertEqual(start.date(), datetime(2026, 3, 9).date())
            self.assertEqual(end.date(), datetime(2026, 3, 15).date())

    def test_generate_date_range(self):
        start = datetime(2026, 3, 10)
        end = datetime(2026, 3, 12)
        dates = main.generate_date_range(start, end)
        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0].date(), datetime(2026, 3, 10).date())
        self.assertEqual(dates[1].date(), datetime(2026, 3, 11).date())
        self.assertEqual(dates[2].date(), datetime(2026, 3, 12).date())


class MainIntegrationTest(unittest.TestCase):
    def test_main_runs_without_error(self):
        try:
            main.main()
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_with_specific_date(self):
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

    @patch('main.is_monday')
    @patch('main.notifiers.get_notifier')
    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_monday_no_games_no_weekly(self, mock_get_games, mock_get_notifier, mock_is_monday):
        mock_is_monday.return_value = True
        mock_get_games.return_value = []  # No games all week
        mock_notifier_instance = MagicMock()
        mock_get_notifier.return_value = mock_notifier_instance

        main.main()

        mock_notifier_instance.send.assert_not_called()

    @patch('main.is_monday')
    @patch('main.notifiers.get_notifier')
    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_monday_with_games_no_goals(self, mock_get_games, mock_get_notifier, mock_is_monday):
        mock_is_monday.return_value = True
        mock_get_games.return_value = [{"id": 12345}]  # Some games but no 4:20 goals
        mock_notifier_instance = MagicMock()
        mock_get_notifier.return_value = mock_notifier_instance

        main.main()

        mock_notifier_instance.send.assert_called_once()

    @patch('main.is_monday')
    @patch('main.notifiers.get_notifier')
    @patch.object(nhl_client.NHLClient, 'get_all_plays')
    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_monday_with_games_and_goals(self, mock_get_games, mock_get_plays, mock_get_notifier, mock_is_monday):
        mock_is_monday.return_value = True
        mock_get_games.return_value = [
            {"id": 12345, "homeTeam": {"commonName": {"default": "A"}, "id": 1}, 
             "awayTeam": {"commonName": {"default": "B"}, "id": 2},
             "startTimeUTC": "2026-03-15T20:00:00Z"}
        ]
        mock_get_plays.return_value = [
            {"typeDescKey": "goal", "timeInPeriod": "04:20", "timeRemaining": "15:40",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 1}}
        ]
        mock_notifier_instance = MagicMock()
        mock_get_notifier.return_value = mock_notifier_instance

        main.main()

        self.assertEqual(mock_notifier_instance.send.call_count, 2)

    @patch('main.is_monday')
    @patch('main.notifiers.get_notifier')
    @patch.object(nhl_client.NHLClient, 'get_all_plays')
    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_non_monday_with_goals(self, mock_get_games, mock_get_plays, mock_get_notifier, mock_is_monday):
        mock_is_monday.return_value = False
        mock_get_games.return_value = [
            {"id": 12345, "homeTeam": {"commonName": {"default": "A"}, "id": 1},
             "awayTeam": {"commonName": {"default": "B"}, "id": 2},
             "startTimeUTC": "2026-03-18T20:00:00Z"}
        ]
        mock_get_plays.return_value = [
            {"typeDescKey": "goal", "timeInPeriod": "04:20", "timeRemaining": "15:40",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 1}}
        ]
        mock_notifier_instance = MagicMock()
        mock_get_notifier.return_value = mock_notifier_instance

        main.main()

        mock_notifier_instance.send.assert_called_once()


class HelperFunctionDirectTest(unittest.TestCase):
    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_check_week_had_games_true(self, mock_get_games):
        mock_get_games.side_effect = [
            [{"id": 1}],  # day 1
            [],           # day 2 (no games)
            [{"id": 2}, {"id": 3}],  # day 3
        ]
        client = nhl_client.NHLClient()
        start = datetime(2026, 3, 10)
        end = datetime(2026, 3, 12)
        
        had_games, total = main.check_week_had_games(client, start, end)
        
        self.assertTrue(had_games)
        self.assertEqual(total, 3)

    @patch.object(nhl_client.NHLClient, 'get_games_for_date')
    def test_check_week_had_games_false(self, mock_get_games):
        mock_get_games.return_value = []
        client = nhl_client.NHLClient()
        start = datetime(2026, 3, 10)
        end = datetime(2026, 3, 12)
        
        had_games, total = main.check_week_had_games(client, start, end)
        
        self.assertFalse(had_games)
        self.assertEqual(total, 0)


if __name__ == "__main__":
    unittest.main()
