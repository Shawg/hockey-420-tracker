#!/usr/bin/env python3
"""
Search all games on Oct 19, 2025 for goals with timeRemaining == "04:20".
"""

import logging
from datetime import datetime
import nhl_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = nhl_client.NHLClient()
date = datetime(2025, 10, 19)
games = client.get_games_for_date(date)

found = False
for game in games:
    game_id = game.get("id")
    if not game_id:
        continue
    
    plays = client.get_all_plays(game_id)
    for play in plays:
        if play.get("typeDescKey") == "goal":
            time_remaining = play.get("timeRemaining", "")
            if time_remaining == "04:20":
                found = True
                time_in_period = play.get("timeInPeriod", "")
                scorer_id = play.get("details", {}).get("scoringPlayerId", 0)
                scorer = client.get_player_name(scorer_id)
                logger.info(f"FOUND: Game {game_id}, Goal by {scorer}")
                logger.info(f"  timeRemaining: {time_remaining}")
                logger.info(f"  timeInPeriod: {time_in_period}")
                # Print full play info for debugging
                logger.info(f"  Full play keys: {list(play.keys())}")

if not found:
    logger.info("No goals with timeRemaining == '04:20' found on Oct 19, 2025")