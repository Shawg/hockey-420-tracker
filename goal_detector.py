"""
Goal detector for identifying 4:20 goals in NHL games.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

TARGET_TIME = "04:20"


class GoalDetector:
    """Detects goals scored at specific times in NHL games."""

    def __init__(self, target_time: str = TARGET_TIME):
        self.target_time = target_time

    def find_420_goals(
        self,
        plays: List[Dict[str, Any]],
        home_team: str,
        away_team: str,
        home_id: int = 0,
        away_id: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find all goals scored at exactly 4:20 in any period.
        Checks both elapsed time (timeInPeriod) and remaining time (timeRemaining).

        Args:
            plays: List of plays from play-by-play data.
            home_team: Name of the home team.
            away_team: Name of the away team.
            home_id: ID of the home team.
            away_id: ID of the away team.

        Returns:
            List of goal dictionaries with details.
        """
        goals_420 = []

        for play in plays:
            if not self._is_goal(play):
                continue

            time_in_period = play.get("timeInPeriod", "")
            time_remaining = play.get("timeRemaining", "")
            
            # Check for 4:20 elapsed OR 4:20 remaining
            is_420_elapsed = time_in_period == self.target_time
            is_420_remaining = time_remaining == self.target_time
            
            if is_420_elapsed or is_420_remaining:
                time_condition = "elapsed" if is_420_elapsed else "remaining"
                goal_info = self._extract_goal_info(
                    play, home_team, away_team, home_id, away_id, time_condition
                )
                goals_420.append(goal_info)
                logger.info(
                    f"Found 4:20 goal: {goal_info['team']} - "
                    f"Period {goal_info['period']} - "
                    f"{time_condition} time"
                )

        return goals_420

    def _is_goal(self, play: Dict[str, Any]) -> bool:
        """Check if a play is a goal."""
        event_type = play.get("typeDescKey", "")
        return event_type == "goal"

    def _extract_goal_info(
        self,
        play: Dict[str, Any],
        home_team: str,
        away_team: str,
        home_id: int = 0,
        away_id: int = 0,
        time_condition: str = "elapsed"
    ) -> Dict[str, Any]:
        """Extract relevant information from a goal play."""
        details = play.get("details", {})
        team_id = details.get("eventOwnerTeamId", 0)

        goal_team = home_team
        opponent = away_team
        if team_id != home_id:
            goal_team = away_team
            opponent = home_team

        period_desc = play.get("periodDescriptor", {})
        period = period_desc.get("number", 1)
        period_ordinal = self._get_period_ordinal(period)

        scorer_id = details.get("scoringPlayerId", 0)
        scorer = f"Player #{scorer_id}"

        assists = []
        if details.get("assist1PlayerId"):
            assists.append(f"Player #{details['assist1PlayerId']}")
        if details.get("assist2PlayerId"):
            assists.append(f"Player #{details['assist2PlayerId']}")
        assists_str = ", ".join(assists) if assists else "None"

        # Determine which time to display based on condition
        if time_condition == "remaining":
            time_display = f"{play.get('timeRemaining', '')} remaining"
        else:
            time_display = play.get("timeInPeriod", "")

        return {
            "team": goal_team,
            "opponent": opponent,
            "period": period_ordinal,
            "time": time_display,
            "scorer": scorer,
            "assists": assists_str,
            "condition": time_condition
        }

    def _get_period_ordinal(self, period: int) -> str:
        """Convert period number to ordinal string."""
        ordinals = {
            1: "1st",
            2: "2nd",
            3: "3rd",
            4: "OT",
            5: "2OT",
            6: "3OT"
        }
        return ordinals.get(period, f"{period}th")