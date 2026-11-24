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


def enrich_goal_with_player_names(goal: dict, client) -> None:
    """Resolve scorer and assist names from the player IDs on a goal."""
    goal["scorer"] = client.get_player_name(goal.get("scoring_player_id", 0))

    assist_ids = [goal.get("assist1_player_id"), goal.get("assist2_player_id")]
    assists = [client.get_player_name(player_id) for player_id in assist_ids if player_id]
    goal["assists"] = ", ".join(assists) if assists else "None"


def get_yesterday() -> datetime:
    """Get yesterday's date."""
    return datetime.now() - timedelta(days=1)


def is_monday() -> bool:
    """Check if today is Monday."""
    return datetime.now().weekday() == 0


def get_week_date_range() -> tuple:
    """Get previous Monday-Sunday range (start of week to yesterday)."""
    today = datetime.now()
    week_end = today - timedelta(days=1)
    week_start = today - timedelta(days=7)
    return week_start, week_end


def generate_date_range(start: datetime, end: datetime) -> list:
    """Generate list of dates from start to end (inclusive)."""
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def check_week_had_games(client, start: datetime, end: datetime) -> tuple:
    """
    Check if any NHL games were played during the date range.
    
    Returns:
        tuple: (had_games: bool, total_games: int)
    """
    total_games = 0
    for date in generate_date_range(start, end):
        games = client.get_games_for_date(date)
        total_games += len(games)
    
    return total_games > 0, total_games


def collect_weekly_goals(client, detector, start: datetime, end: datetime) -> list:
    """
    Collect all 4:20 goals from the date range.
    
    Returns:
        list: List of goal dictionaries with game_date set
    """
    all_goals = []
    
    for date in generate_date_range(start, end):
        games = client.get_games_for_date(date)
        
        for game in games:
            game_id = game.get("id")
            if not game_id:
                continue

            # Each game was fetched from this day's schedule entry, so the
            # game day is the alert date. startTimeUTC rolls over to the next
            # UTC date for evening games and would mislabel them.
            game_date = date.strftime("%Y-%m-%d")

            teams = client.get_game_teams(game)
            plays = client.get_all_plays(game_id)
            
            goals = detector.find_420_goals(
                plays,
                teams["home"],
                teams["away"],
                int(teams.get("home_id", 0)),
                int(teams.get("away_id", 0))
            )
            
            for goal in goals:
                goal["game_date"] = game_date
                enrich_goal_with_player_names(goal, client)

            all_goals.extend(goals)
    
    return all_goals


def main():
    """Main function to check for 4:20 goals."""
    logger.info("Starting 4:20 Goal Tracker")

    client = nhl_client.NHLClient()
    detector = goal_detector.GoalDetector()
    notifier = notifiers.get_notifier()

    # PART 1: Monday weekly summary logic
    if is_monday():
        logger.info("Today is Monday - checking weekly summary")
        week_start, week_end = get_week_date_range()
        week_start_str = week_start.strftime("%B %-d")
        week_end_str = week_end.strftime("%B %-d, %Y")
        
        had_games, total_games = check_week_had_games(client, week_start, week_end)
        
        if had_games:
            logger.info(f"Found {total_games} games this week - checking for 4:20 goals")
            weekly_goals = collect_weekly_goals(client, detector, week_start, week_end)
            
            message = notifier.format_weekly_summary(
                week_start_str, week_end_str, total_games, weekly_goals
            )
            success = notifier.send(message)
            if success:
                logger.info(f"Weekly summary sent with {len(weekly_goals)} goal(s)")
            else:
                logger.error("Failed to send weekly summary")
        else:
            logger.info("No games this week, skipping weekly summary")

    # PART 2: Daily goal detection (all days including Monday)
    target_date = get_yesterday()
    logger.info(f"Checking games from {target_date.strftime('%Y-%m-%d')}")

    games = client.get_games_for_date(target_date)

    if not games:
        logger.info("No games found for yesterday, skipping daily notification")
        return

    all_420_goals = []
    all_goalie_goals = []

    for game in games:
        game_id = game.get("id")
        if not game_id:
            continue

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
            enrich_goal_with_player_names(goal, client)

        all_420_goals.extend(goals_420)

        goalie_goals = detector.find_goalie_goals(
            plays,
            client,
            teams["home"],
            teams["away"],
            int(teams.get("home_id", 0)),
            int(teams.get("away_id", 0))
        )

        for goal in goalie_goals:
            goal["game_date"] = game_date
            enrich_goal_with_player_names(goal, client)

        all_goalie_goals.extend(goalie_goals)

    logger.info(f"Found {len(all_420_goals)} total 4:20 goals")
    logger.info(f"Found {len(all_goalie_goals)} total goalie goals")

    if all_420_goals or all_goalie_goals:
        message = notifier.format_goal_message(all_420_goals, all_goalie_goals)
        success = notifier.send(message)
        if success:
            logger.info("Daily alert sent successfully")
        else:
            logger.error("Failed to send daily alert")
    else:
        logger.info("No 4:20 goals or goalie goals found, staying silent")


if __name__ == "__main__":
    main()
