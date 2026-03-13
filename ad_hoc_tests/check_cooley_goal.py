#!/usr/bin/env python3
"""
Check for Cooley 4:20 goal in Bruins @ Mammoth game on Oct 19, 2025.
"""

import logging
from datetime import datetime
import nhl_client
import goal_detector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

client = nhl_client.NHLClient()
detector = goal_detector.GoalDetector()

# Game ID from earlier output
game_id = 2025020092

logger.info(f"Fetching play-by-play for game {game_id}")
plays = client.get_all_plays(game_id)
logger.info(f"Total plays: {len(plays)}")

# Get team info
games = client.get_games_for_date(datetime(2025, 10, 19))
for game in games:
    if game.get("id") == game_id:
        teams = client.get_game_teams(game)
        logger.info(f"Teams: {teams}")
        break

# Find all goals
goals = [p for p in plays if p.get("typeDescKey") == "goal"]
logger.info(f"Total goals in game: {len(goals)}")

for i, goal in enumerate(goals):
    time_in_period = goal.get("timeInPeriod", "")
    period = goal.get("periodDescriptor", {}).get("number", 0)
    details = goal.get("details", {})
    scorer_id = details.get("scoringPlayerId", 0)
    scorer = client.get_player_name(scorer_id)
    
    logger.info(f"Goal {i+1}: Period {period}, Time {time_in_period}, Scorer: {scorer}")
    if time_in_period == "4:20":
        logger.info("  >>> THIS IS A 4:20 GOAL!")
        logger.info(f"  Full goal data: {goal}")

# Now run the detector
goals_420 = detector.find_420_goals(
    plays,
    teams["home"],
    teams["away"],
    int(teams.get("home_id", 0)),
    int(teams.get("away_id", 0))
)
logger.info(f"Detector found {len(goals_420)} 4:20 goals")

for g in goals_420:
    logger.info(g)