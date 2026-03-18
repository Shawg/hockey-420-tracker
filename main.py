#!/usr/bin/env python3
"""
Main entry point for the 4:20 Goal Tracker.
Checks yesterday's NHL games for goals scored at exactly 4:20.
"""

import logging
from datetime import datetime, timedelta

import nhl_client
import goal_detector
import notifiers
import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_yesterday() -> datetime:
    """Get yesterday's date."""
    return datetime.now() - timedelta(days=1)


def main():
    """Main function to check for 4:20 goals."""
    logger.info("Starting 4:20 Goal Tracker")

    target_date = get_yesterday()
    logger.info(f"Checking games from {target_date.strftime('%Y-%m-%d')}")

    client = nhl_client.NHLClient()
    detector = goal_detector.GoalDetector()

    games = client.get_games_for_date(target_date)

    if not games:
        logger.info("No games found for yesterday, skipping notification")
        return

    all_420_goals = []

    for game in games:
        game_id = game.get("id")
        if not game_id:
            continue

        game_date = game.get("startTimeUTC", "")
        if game_date:
            try:
                game_date = datetime.fromisoformat(game_date.replace("Z", "+00:00")).strftime("%Y-%m-%d")
            except Exception:
                game_date = target_date.strftime("%Y-%m-%d")
        else:
            game_date = target_date.strftime("%Y-%m-%d")

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
            goal["game_date"] = game_date
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

    notifier = notifiers.get_notifier()
    message = notifier.format_goal_message(all_420_goals)

    success = notifier.send(message)

    if success:
        logger.info("Notification sent successfully")
    else:
        logger.error("Failed to send notification")


if __name__ == "__main__":
    main()
