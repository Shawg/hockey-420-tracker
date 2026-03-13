#!/usr/bin/env python3
"""
Test script to check for 4:20 goals between October 15-25, 2025.
"""

import logging
from datetime import datetime, timedelta
import nhl_client
import goal_detector

# Set up logging to print to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_date_range(start_date, end_date):
    """Test for 4:20 goals in a date range."""
    client = nhl_client.NHLClient()
    detector = goal_detector.GoalDetector()
    
    total_goals = 0
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing date: {date_str}")
        logger.info(f"{'='*50}")
        
        games = client.get_games_for_date(current_date)
        
        if not games:
            logger.info(f"No games found for {date_str}")
            current_date += timedelta(days=1)
            continue
        
        day_goals = []
        
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
                # Get player names (as in main.py)
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
                
                day_goals.append(goal)
        
        if day_goals:
            logger.info(f"✅ Found {len(day_goals)} 4:20 goal(s) on {date_str}:")
            for goal in day_goals:
                logger.info(f"  - {goal['team']} vs {goal['opponent']} | "
                           f"Period: {goal['period']} | Scorer: {goal['scorer']} | "
                           f"Assists: {goal['assists']}")
            total_goals += len(day_goals)
        else:
            logger.info(f"❌ No 4:20 goals found on {date_str}")
        
        current_date += timedelta(days=1)
    
    logger.info(f"\n{'='*50}")
    logger.info(f"TOTAL 4:20 GOALS IN RANGE: {total_goals}")
    logger.info(f"{'='*50}")
    return total_goals

if __name__ == "__main__":
    # October 15-25, 2025
    start = datetime(2025, 10, 15)
    end = datetime(2025, 10, 25)
    
    test_date_range(start, end)