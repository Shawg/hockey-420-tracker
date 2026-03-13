#!/usr/bin/env python3
"""
Check for any goals with timeRemaining == "04:20" in the Cooley game.
"""

import logging
import nhl_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = nhl_client.NHLClient()
game_id = 2025020092  # Bruins @ Mammoth
plays = client.get_all_plays(game_id)

for play in plays:
    if play.get("typeDescKey") == "goal":
        time_in_period = play.get("timeInPeriod", "")
        time_remaining = play.get("timeRemaining", "")
        scorer_id = play.get("details", {}).get("scoringPlayerId", 0)
        scorer = client.get_player_name(scorer_id)
        
        logger.info(f"Goal by {scorer}: timeInPeriod='{time_in_period}', timeRemaining='{time_remaining}'")