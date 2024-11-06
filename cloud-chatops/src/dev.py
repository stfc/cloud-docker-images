"""This module runs local integration tests of the code."""

import logging
import argparse
from argparse import Namespace
from errors import NoTestCase
from read_data import validate_required_files
from events import run_global_reminder, run_personal_reminder

logging.basicConfig(level=logging.DEBUG)
args = None


def run_tests() -> None:
    """
    Test each event given in args.
    """
    [call_test(arg) for arg, value in vars(args).items() if value]


def call_test(event: str) -> None:
    """
    Run the test logic for each event.
    :param event: The event to test
    """
    match event:
        case "channel":
            """
            Catch case for the required parameter "channel".
            Nothing should run here as channel is an arg of other tests
            """
        case "global":
            run_global_reminder(args.channel)
        case "personal":
            run_personal_reminder()
        case _:
            raise NoTestCase(f"There is not test case for {event}")


def main() -> None:
    """
    This function checks the config files, runs the tests then starts the application.
    :param app: Async app to run Slack app
    """
    validate_required_files()
    logging.info("Running tests\n")
    run_tests()
    logging.info("Completed tests.\n")


def parse_args() -> Namespace:
    """Create and collect arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", help="Channel to send messages to.")
    parser.add_argument(
        "--global", help="Test the global reminder", action="store_true"
    )
    parser.add_argument(
        "--personal", help="Test the personal reminder", action="store_true"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main()
