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
            return "No 4:20 goals found for yesterday's games. 😔"

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