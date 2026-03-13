import unittest
from datetime import datetime, timedelta
import nhl_client


class NHLClientIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = nhl_client.NHLClient()

    def test_fetch_yesterday_games(self):
        date = datetime.now() - timedelta(days=1)
        games = self.client.get_games_for_date(date)
        # we can't assert a fixed number, but it should be a list
        self.assertIsInstance(games, list)
        # every game returned should have an id and startTimeUTC matching the date
        for g in games:
            self.assertIn("id", g)
            self.assertIn("startTimeUTC", g)
            game_dt = datetime.fromisoformat(g["startTimeUTC"].replace("Z", "+00:00"))
            self.assertEqual(game_dt.date(), date.date())

    def test_get_play_by_play(self):
        date = datetime.now() - timedelta(days=1)
        games = self.client.get_games_for_date(date)
        if not games:
            self.skipTest("no games yesterday")
        game_id = games[0].get("id")
        pbp = self.client.get_play_by_play(game_id)
        self.assertIsInstance(pbp, dict)
        self.assertIn("plays", pbp)


if __name__ == "__main__":
    unittest.main()
