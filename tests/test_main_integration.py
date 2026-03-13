import unittest
from datetime import datetime, timedelta
import main
import nhl_client


class MainIntegrationTest(unittest.TestCase):
    def test_main_runs_without_error(self):
        # run the main function; it will fetch yesterday's games and
        # send a notification (config must be set, else notifier may fail).
        # We just ensure it completes without raising.
        try:
            main.main()
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_main_with_specific_date(self):
        # monkey patch get_yesterday to use a fixed date
        original = main.get_yesterday
        target = datetime.now() - timedelta(days=1)
        main.get_yesterday = lambda: target
        try:
            main.main()
        finally:
            main.get_yesterday = original


if __name__ == "__main__":
    unittest.main()
