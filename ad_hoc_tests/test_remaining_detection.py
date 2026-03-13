#!/usr/bin/env python3
"""
Test detection of 4:20 remaining goal (Owen Tippett).
"""

import logging
from datetime import datetime
import nhl_client
import goal_detector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = nhl_client.NHLClient()
detector = goal_detector.GoalDetector()

# Game with Tippett 4:20 remaining goal
game_id = 2025020094
games = client.get_games_for_date(datetime(2025, 10, 19))
target_game = None
for game in games:
    if game.get("id") == game_id:
        target_game = game
        break

if not target_game:
    logger.error(f"Game {game_id} not found")
    exit(1)

teams = client.get_game_teams(target_game)
logger.info(f"Testing game: {teams['away']} @ {teams['home']}")

plays = client.get_all_plays(game_id)
goals_420 = detector.find_420_goals(
    plays,
    teams["home"],
    teams["away"],
    int(teams.get("home_id", 0)),
    int(teams.get("away_id", 0))
)

logger.info(f"Found {len(goals_420)} 4:20 goals")
for goal in goals_420:
    logger.info(f"Goal: {goal}")
    
    # Get scorer name (detector only returns Player #ID)
    matching_plays = [
        p for p in plays 
        if p.get("typeDescKey") == "goal" and p.get("timeRemaining") == goal["time"]
    ]
    if matching_plays:
        d = matching_plays[0].get("details", {})
        scorer_id = d.get("scoringPlayerId", 0)
        scorer = client.get_player_name(scorer_id)
        logger.info(f"  Actual scorer: {scorer}")
        # Update goal info for notification
        goal["scorer"] = scorer
        assists = []
        if d.get("assist1PlayerId"):
            assists.append(client.get_player_name(d["assist1PlayerId"]))
        if d.get("assist2PlayerId"):
            assists.append(client.get_player_name(d["assist2PlayerId"]))
        goal["assists"] = ", ".join(assists) if assists else "None"