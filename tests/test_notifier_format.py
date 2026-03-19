import unittest
from notifiers.base import Notifier


class DummyNotifier(Notifier):
    def send(self, message: str) -> bool:
        return True


class NotifierFormatTest(unittest.TestCase):
    def setUp(self):
        self.notifier = DummyNotifier()

    def test_empty_list(self):
        msg = self.notifier.format_goal_message([])
        self.assertEqual(msg, "")

    def test_multiple_goals(self):
        goals = [
            {"team": "A", "opponent": "B", "period": "1st", "time": "04:20", "scorer": "Player 1", "assists": "None"},
            {"team": "C", "opponent": "D", "period": "2nd", "time": "04:20", "scorer": "Player 2", "assists": "P1"},
        ]
        msg = self.notifier.format_goal_message(goals)
        self.assertIn("Total: 2 goal(s)", msg)
        self.assertRegex(msg, r"A\W+vs\W+B")
        self.assertIn("Scorer: Player 1", msg)

    def test_date_in_message(self):
        goals = [{"team": "A", "opponent": "B", "period": "1st", "time": "04:20",
                 "scorer": "Player 1", "assists": "None", "game_date": "2026-03-12"}]
        msg = self.notifier.format_goal_message(goals)
        self.assertIn("2026-03-12", msg)

    def test_date_header_format(self):
        goals = [{"team": "A", "opponent": "B", "period": "1st", "time": "04:20",
                 "scorer": "Player 1", "assists": "None", "game_date": "2026-03-12"}]
        msg = self.notifier.format_goal_message(goals)
        self.assertRegex(msg, r"4:20 GOAL.*2026-03-12")

    def test_weekly_summary_no_goals(self):
        msg = self.notifier.format_weekly_summary(
            "March 10", "March 16, 2026", 42, []
        )
        self.assertIn("March 10", msg)
        self.assertIn("March 16, 2026", msg)
        self.assertIn("42", msg)
        self.assertIn("No 4:20 goals", msg)

    def test_weekly_summary_with_goals(self):
        goals = [
            {"team": "A", "opponent": "B", "period": "1st", "time": "04:20",
             "scorer": "Player 1", "assists": "None", "game_date": "2026-03-12"},
            {"team": "C", "opponent": "D", "period": "2nd", "time": "04:20",
             "scorer": "Player 2", "assists": "P1", "game_date": "2026-03-14"},
        ]
        msg = self.notifier.format_weekly_summary(
            "March 10", "March 16, 2026", 50, goals
        )
        self.assertIn("March 10", msg)
        self.assertIn("March 16, 2026", msg)
        self.assertIn("50", msg)
        self.assertIn("2 total 4:20 goal(s)", msg)
        self.assertIn("2026-03-12", msg)
        self.assertIn("2026-03-14", msg)
        self.assertIn("Player 1", msg)
        self.assertIn("Player 2", msg)


if __name__ == "__main__":
    unittest.main()
