#!/usr/bin/env python3
"""
Check the exact time format in NHL API for the Cooley goal.
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
        period_desc = play.get("periodDescriptor", {})
        period = period_desc.get("number", 0)
        details = play.get("details", {})
        scorer_id = details.get("scoringPlayerId", 0)
        scorer = client.get_player_name(scorer_id)
        
        logger.info(f"Goal by {scorer} - Period {period}, timeInPeriod: '{time_in_period}'")
        # Print all keys in play to see if there's a "timeRemaining" field
        logger.info(f"  Play keys: {list(play.keys())}")
        if "details" in play:
            logger.info(f"  Details keys: {list(play['details'].keys())}")
        # Print a sample of the play (first few keys)
        for key, value in play.items():
            if isinstance(value, (str, int, float)):
                logger.info(f"  {key}: {value}")
        break  # just one goal