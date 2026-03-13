#!/usr/bin/env python3
"""
Test the full detection and notification for Oct 19, 2025.
"""

import logging
from datetime import datetime
import nhl_client
import goal_detector
import notifiers

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

target_date = datetime(2025, 10, 19)
logger.info(f"Checking games from {target_date.strftime('%Y-%m-%d')}")

client = nhl_client.NHLClient()
detector = goal_detector.GoalDetector()

games = client.get_games_for_date(target_date)

all_420_goals = []

for game in games:
    game_id = game.get("id")
    if not game_id:
        continue

    teams = client.get_game_teams(game)
    logger.info(f"Checking game {game_id}: {teams['away']} @ {teams['home']}")

    plays = client.get_all_plays(game_id)

    goals_420 = detector.find_420_goals(
        plays,
        teams["home"],
        teams["away"],
        int(teams.get("home_id", 0)),
        int(teams.get("away_id", 0))
    )

    for goal in goals_420:
        matching_plays = [
            p for p in plays 
            if p.get("typeDescKey") == "goal" and p.get("timeInPeriod") == goal["time"]
        ]
        if matching_plays:
            d = matching_plays[0].get("details", {})
            scorer_id = d.get("scoringPlayerId", 0)
            goal["scorer"] = client.get_player_name(scorer_id)
            
            assists = []
            if d.get("assist1PlayerId"):
                assists.append(client.get_player_name(d["assist1PlayerId"]))
            if d.get("assist2PlayerId"):
                assists.append(client.get_player_name(d["assist2PlayerId"]))
            goal["assists"] = ", ".join(assists) if assists else "None"

        all_420_goals.extend(goals_420)

logger.info(f"Found {len(all_420_goals)} total 4:20 goals")

if all_420_goals:
    # Get a notifier (using test config)
    notifier = notifiers.get_notifier()
    message = notifier.format_goal_message(all_420_goals)
    logger.info("Formatted message:")
    logger.info(message)
else:
    logger.info("No 4:20 goals to notify.")