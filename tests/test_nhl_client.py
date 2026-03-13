import unittest
from datetime import datetime

import nhl_client


class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


class NHLClientTest(unittest.TestCase):
    def test_get_games_for_date_filters_week(self):
        # prepare fake schedule: two games, one on target date and one later
        date = datetime(2026, 3, 11)
        schedule = {
            "gameWeek": [
                {
                    "games": [
                        {"id": 1, "startTimeUTC": "2026-03-11T20:00:00Z"},
                        {"id": 2, "startTimeUTC": "2026-03-14T20:00:00Z"},
                    ]
                }
            ]
        }

        client = nhl_client.NHLClient()

        # monkeypatch the session.get method to return our dummy response
        def fake_get(url, timeout):
            return DummyResponse(schedule)

        client.session.get = fake_get

        games = client.get_games_for_date(date)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["id"], 1)


if __name__ == "__main__":
    unittest.main()
