"""
NHL API Client for fetching game data and play-by-play information.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)

SCHEDULE_URL = "https://api-web.nhle.com/v1/schedule"
PLAY_BY_PLAY_URL = "https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play"


class NHLClient:
    """Client for interacting with the NHL public API."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Hockey420Tracker/1.0"
        })

    def get_date_string(self, date: datetime) -> str:
        """Convert datetime to YYYY-MM-DD format for API."""
        return date.strftime("%Y-%m-%d")

    def get_games_for_date(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Fetch all games for a given date.

        Args:
            date: The date to fetch games for.

        Returns:
            List of game data dictionaries.
        """
        date_str = self.get_date_string(date)
        url = f"{SCHEDULE_URL}/{date_str}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            all_games = []
            for game_week in data.get("gameWeek", []):
                for day in game_week.get("games", []):
                    all_games.append(day)

            # The NHL schedule endpoint returns an entire "gameWeek" (roughly a
            # 7-day span) rather than strictly the single date requested.  that
            # means when you ask for e.g. 2026-03-11 you'll also get games on
            # 2026-03-14, etc.  our tracker is only supposed to look at games
            # that actually occurred on the target date, so filter accordingly.
            filtered = []
            for g in all_games:
                start = g.get("startTimeUTC")
                if not start:
                    # just in case the API response is missing the field,
                    # include the game to avoid silently dropping it
                    filtered.append(g)
                    continue
                try:
                    game_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                except Exception:
                    filtered.append(g)
                    continue
                if game_dt.date() == date.date():
                    filtered.append(g)

            logger.info(f"Found {len(filtered)} games for {date_str} (filtered from {len(all_games)})")
            return filtered
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch schedule for {date_str}: {e}")
            return []

    def get_play_by_play(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch play-by-play data for a specific game.

        Args:
            game_id: The NHL game ID.

        Returns:
            Play-by-play data dictionary or None if failed.
        """
        url = PLAY_BY_PLAY_URL.format(game_id=game_id)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch play-by-play for game {game_id}: {e}")
            return None

    def get_all_plays(self, game_id: int) -> List[Dict[str, Any]]:
        """
        Get all plays from a game's play-by-play data.

        Args:
            game_id: The NHL game ID.

        Returns:
            List of play dictionaries.
        """
        pbp_data = self.get_play_by_play(game_id)
        if pbp_data:
            return pbp_data.get("plays", [])
        return []

    def get_game_teams(self, game: Dict[str, Any]) -> Dict[str, str]:
        """Extract home and away team names from game data."""
        return {
            "home": game.get("homeTeam", {}).get("commonName", {}).get("default", "Unknown"),
            "away": game.get("awayTeam", {}).get("commonName", {}).get("default", "Unknown"),
            "home_id": game.get("homeTeam", {}).get("id", 0),
            "away_id": game.get("awayTeam", {}).get("id", 0)
        }

    def get_player_name(self, player_id: int) -> str:
        """Get player name from player ID."""
        url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                first = data.get("firstName", {}).get("default", "")
                last = data.get("lastName", {}).get("default", "")
                return f"{first} {last}".strip()
        except Exception:
            pass
        return f"Player #{player_id}"

    def get_player_position(self, player_id: int) -> str:
        """Get player position (G, D, F, etc.) from player ID."""
        url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("position", "")
        except Exception:
            pass
        return ""