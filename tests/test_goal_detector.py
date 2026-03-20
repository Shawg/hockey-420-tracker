import unittest
from goal_detector import GoalDetector


class GoalDetectorUnitTest(unittest.TestCase):
    def setUp(self):
        self.detector = GoalDetector()
        self.home = "HomeTeam"
        self.away = "AwayTeam"

    def make_goal(self, time_in, time_rem, team_id, home_id=1, away_id=2):
        # minimal structure emulating API play
        return {
            "typeDescKey": "goal",
            "timeInPeriod": time_in,
            "timeRemaining": time_rem,
            "details": {"eventOwnerTeamId": team_id, "scoringPlayerId": 10},
            "periodDescriptor": {"number": 1}
        }

    def test_detect_elapsed_time(self):
        plays = [self.make_goal("04:20", "15:00", team_id=1)]
        goals = self.detector.find_420_goals(plays, self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["time"], "04:20")
        self.assertEqual(goals[0]["condition"], "elapsed")

    def test_detect_remaining_time(self):
        plays = [self.make_goal("10:00", "04:20", team_id=2)]
        goals = self.detector.find_420_goals(plays, self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertIn("remaining", goals[0]["time"])
        self.assertEqual(goals[0]["condition"], "remaining")

    def test_ignore_non_goal(self):
        plays = [{"typeDescKey": "shot", "timeInPeriod": "04:20", "timeRemaining": "04:20"}]
        goals = self.detector.find_420_goals(plays, self.home, self.away)
        self.assertEqual(goals, [])

    def test_ot_period(self):
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "04:20", "timeRemaining": "15:40",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 4}}  # OT
        ]
        goals = self.detector.find_420_goals(plays, self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["period"], "OT")

    def test_2ot_period(self):
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "04:20", "timeRemaining": "15:40",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 5}}  # 2OT
        ]
        goals = self.detector.find_420_goals(plays, self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["period"], "2OT")

    def test_3ot_period(self):
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "04:20", "timeRemaining": "15:40",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 6}}  # 3OT
        ]
        goals = self.detector.find_420_goals(plays, self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["period"], "3OT")


    def test_find_goalie_goals_detects_goalie(self):
        class MockClient:
            def get_player_position(self, player_id):
                if player_id == 10:
                    return "G"
                return "F"
        
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "10:00",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 1}}
        ]
        goals = self.detector.find_goalie_goals(plays, MockClient(), self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["team"], "HomeTeam")
        self.assertEqual(goals[0]["period"], "1st")

    def test_find_goalie_goals_ignores_regular_player(self):
        class MockClient:
            def get_player_position(self, player_id):
                return "F"
        
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "10:00",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 1}}
        ]
        goals = self.detector.find_goalie_goals(plays, MockClient(), self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 0)

    def test_find_goalie_goals_empty_plays(self):
        class MockClient:
            def get_player_position(self, player_id):
                return "G"
        
        plays = []
        goals = self.detector.find_goalie_goals(plays, MockClient(), self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 0)

    def test_find_goalie_goals_multiple(self):
        class MockClient:
            def get_player_position(self, player_id):
                if player_id in [10, 20]:
                    return "G"
                return "F"
        
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "10:00",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 1}},
            {"typeDescKey": "goal", "timeInPeriod": "15:00",
             "details": {"eventOwnerTeamId": 2, "scoringPlayerId": 20},
             "periodDescriptor": {"number": 2}},
            {"typeDescKey": "goal", "timeInPeriod": "05:00",
             "details": {"eventOwnerTeamId": 1, "scoringPlayerId": 30},
             "periodDescriptor": {"number": 3}}
        ]
        goals = self.detector.find_goalie_goals(plays, MockClient(), self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 2)
        self.assertEqual(goals[0]["team"], "HomeTeam")
        self.assertEqual(goals[1]["team"], "AwayTeam")

    def test_find_goalie_goals_away_team(self):
        class MockClient:
            def get_player_position(self, player_id):
                return "G"
        
        plays = [
            {"typeDescKey": "goal", "timeInPeriod": "10:00",
             "details": {"eventOwnerTeamId": 2, "scoringPlayerId": 10},
             "periodDescriptor": {"number": 1}}
        ]
        goals = self.detector.find_goalie_goals(plays, MockClient(), self.home, self.away, home_id=1, away_id=2)
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["team"], "AwayTeam")
        self.assertEqual(goals[0]["opponent"], "HomeTeam")


if __name__ == "__main__":
    unittest.main()
