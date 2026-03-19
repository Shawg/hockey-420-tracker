import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

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

    def format_goal_message(self, goals: List[Dict[str, Any]]) -> str:
        """Format a list of 4:20 goals into a readable message."""
        if not goals:
            return ""

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

        message += f"Total: {len(goals)} goal(s) yesterday!"
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