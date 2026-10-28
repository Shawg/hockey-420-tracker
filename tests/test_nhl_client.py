import unittest
from datetime import datetime
from unittest.mock import patch

import requests

import nhl_client


class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


class NHLClientTest(unittest.TestCase):
    def setUp(self):
        self.client = nhl_client.NHLClient()

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

        # monkeypatch the session.get method to return our dummy response
        def fake_get(url, timeout):
            return DummyResponse(schedule)

        self.client.session.get = fake_get

        games = self.client.get_games_for_date(date)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["id"], 1)

    def test_get_games_for_date_network_error_returns_empty(self):
        def fake_get(url, timeout):
            raise requests.exceptions.RequestException("network down")

        self.client.session.get = fake_get

        games = self.client.get_games_for_date(datetime(2026, 3, 11))
        self.assertEqual(games, [])

    def test_get_games_for_date_keeps_games_without_start_time(self):
        schedule = {"gameWeek": [{"games": [{"id": 1}]}]}

        self.client.session.get = lambda url, timeout: DummyResponse(schedule)

        games = self.client.get_games_for_date(datetime(2026, 3, 11))
        self.assertEqual(len(games), 1)

    def test_get_games_for_date_uses_30s_timeout(self):
        timeouts = []

        def fake_get(url, timeout):
            timeouts.append(timeout)
            return DummyResponse({"gameWeek": []})

        self.client.session.get = fake_get
        self.client.get_games_for_date(datetime(2026, 3, 11))

        self.assertEqual(timeouts, [30])

    def test_player_lookup_uses_10s_timeout(self):
        timeouts = []

        def fake_get(url, timeout):
            timeouts.append(timeout)
            return DummyResponse({"position": "G"})

        self.client.session.get = fake_get
        self.client.get_player_position(8478009)

        self.assertEqual(timeouts, [10])

    @patch.object(nhl_client.NHLClient, 'get_play_by_play', return_value=None)
    def test_get_all_plays_none_returns_empty(self, mock_pbp):
        self.assertEqual(self.client.get_all_plays(123), [])

    @patch.object(nhl_client.NHLClient, 'get_play_by_play', return_value={"plays": [{"a": 1}]})
    def test_get_all_plays_returns_plays(self, mock_pbp):
        self.assertEqual(self.client.get_all_plays(123), [{"a": 1}])

    def test_get_game_teams_extracts_names_and_ids(self):
        game = {
            "homeTeam": {"id": 1, "commonName": {"default": "Maple Leafs"}},
            "awayTeam": {"id": 2, "commonName": {"default": "Canadiens"}},
        }
        teams = self.client.get_game_teams(game)
        self.assertEqual(teams["home"], "Maple Leafs")
        self.assertEqual(teams["away"], "Canadiens")
        self.assertEqual(teams["home_id"], 1)
        self.assertEqual(teams["away_id"], 2)

    def test_get_game_teams_defaults(self):
        teams = self.client.get_game_teams({})
        self.assertEqual(teams["home"], "Unknown")
        self.assertEqual(teams["away"], "Unknown")
        self.assertEqual(teams["home_id"], 0)
        self.assertEqual(teams["away_id"], 0)

    def test_get_player_name_returns_full_name(self):
        self.client.session.get = lambda url, timeout: DummyResponse({
            "firstName": {"default": "Connor"},
            "lastName": {"default": "McDavid"},
        })
        self.assertEqual(self.client.get_player_name(97), "Connor McDavid")

    def test_get_player_name_fallback_on_error(self):
        def fake_get(url, timeout):
            raise requests.exceptions.RequestException("network down")

        self.client.session.get = fake_get
        self.assertEqual(self.client.get_player_name(97), "Player #97")

    def test_get_player_name_fallback_on_non_200(self):
        self.client.session.get = lambda url, timeout: DummyResponse({}, status_code=404)
        self.assertEqual(self.client.get_player_name(97), "Player #97")

    def test_get_player_position_returns_position(self):
        self.client.session.get = lambda url, timeout: DummyResponse({"position": "G"})
        self.assertEqual(self.client.get_player_position(8478009), "G")

    def test_get_player_position_fallback_on_error(self):
        self.client.session.get = lambda url, timeout: DummyResponse({}, status_code=500)
        self.assertEqual(self.client.get_player_position(8478009), "")


if __name__ == "__main__":
    unittest.main()
