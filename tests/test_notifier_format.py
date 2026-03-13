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
        self.assertIn("No 4:20 goals", msg)

    def test_multiple_goals(self):
        goals = [
            {"team": "A", "opponent": "B", "period": "1st", "time": "04:20", "scorer": "Player 1", "assists": "None"},
            {"team": "C", "opponent": "D", "period": "2nd", "time": "04:20", "scorer": "Player 2", "assists": "P1"},
        ]
        msg = self.notifier.format_goal_message(goals)
        self.assertIn("Total: 2 goal(s)", msg)
        # teams may be split by a newline due to Markdown formatting; just
        # verify both names and the "vs" keyword appear in sequence.
        self.assertRegex(msg, r"A\W+vs\W+B")
        self.assertIn("Scorer: Player 1", msg)


if __name__ == "__main__":
    unittest.main()
