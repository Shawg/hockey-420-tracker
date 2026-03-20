import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Notifier(ABC):
    """Abstract base class for notification implementations."""

    @abstractmethod
    def send(self, message: str) -> bool:
        """
        Send a notification message.

        Args:
            message: The message to send.

        Returns:
            True if successful, False otherwise.
        """
        pass

    def format_goal_message(self, goals: List[Dict[str, Any]], goalie_goals: Optional[List[Dict[str, Any]]] = None) -> str:
        """Format 4:20 goals and goalie goals into a readable message."""
        if not goals and not goalie_goals:
            return ""
        
        if goalie_goals is None:
            goalie_goals = []

        has_420 = bool(goals)
        has_goalie = bool(goalie_goals)

        if has_420:
            game_date = goals[0].get("game_date", "")
            if game_date:
                message = f"🎯 **4:20 GOAL ALERT for {game_date}!** 🎯\n\n"
            else:
                message = "🎯 **4:20 GOAL ALERT!** 🎯\n\n"

            for goal in goals:
                message += f"• **{goal['team']}** vs {goal['opponent']}\n"
                message += f"  Period {goal['period']} at {goal['time']}\n"
                message += f"  Scorer: {goal['scorer']}\n"
                if goal.get('assists'):
                    message += f"  Assists: {goal['assists']}\n"
                message += "\n"
        else:
            game_date = goalie_goals[0].get("game_date", "") if goalie_goals else ""
            if game_date:
                message = f"🧤 **GOALIE GOAL ALERT for {game_date}!**\n\n"
            else:
                message = "🧤 **GOALIE GOAL ALERT!**\n\n"

        if has_goalie:
            message += "🧤 **GOALIE GOAL ALERT!**\n\n"
            for goal in goalie_goals:
                message += f"• **{goal['team']}** vs {goal['opponent']}\n"
                message += f"  Period {goal['period']}\n"
                message += f"  Scorer: {goal['scorer']}\n"
                if goal.get('assists'):
                    message += f"  Assists: {goal['assists']}\n"
                message += "\n"

        if has_420 and has_goalie:
            message += f"Total: {len(goals)} 4:20 goal(s) + {len(goalie_goals)} goalie goal(s)!"
        elif has_420:
            message += f"Total: {len(goals)} goal(s) yesterday!"
        else:
            message += f"Total: {len(goalie_goals)} goalie goal(s)!"
        
        return message

    def format_weekly_summary(
        self,
        week_start: str,
        week_end: str,
        total_games: int,
        goals: list = None  # type: ignore[assignment]
    ) -> str:
        """Format a weekly summary message."""
        if goals:
            message = f"📊 Weekly Summary ({week_start} to {week_end})\n"
            message += f"{len(goals)} total 4:20 goal(s) found across {total_games} games!\n\n"
            
            for goal in goals:
                message += f"• {goal.get('game_date', 'Unknown')}: "
                message += f"{goal['team']} vs {goal['opponent']}\n"
                message += f"  Period {goal['period']} at {goal['time']}\n"
                message += f"  Scorer: {goal['scorer']}\n\n"
            
            return message
        else:
            return f"📊 Weekly Summary ({week_start} to {week_end})\nNo 4:20 goals found across {total_games} games played"