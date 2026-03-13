#!/usr/bin/env python3
"""
Check for Utah vs Boston game on Oct 19, 2025.
"""

import logging
from datetime import datetime
import nhl_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = nhl_client.NHLClient()
date = datetime(2025, 10, 19)
games = client.get_games_for_date(date)

logger.info(f"Found {len(games)} games on {date.strftime('%Y-%m-%d')}")

for game in games:
    home = game.get("homeTeam", {})
    away = game.get("awayTeam", {})
    home_name = home.get("commonName", {}).get("default", "")
    away_name = away.get("commonName", {}).get("default", "")
    game_id = game.get("id", 0)
    
    # Print all games
    logger.info(f"Game {game_id}: {away_name} @ {home_name}")
    # Check for Utah or Boston
    if ("Utah" in home_name or "Utah" in away_name or
        "Boston" in home_name or "Boston" in away_name):
        logger.info(f"  >>> Utah/Boston game found!")
        logger.info(f"  Full home: {home}")
        logger.info(f"  Full away: {away}")