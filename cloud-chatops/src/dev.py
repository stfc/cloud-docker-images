"""This module runs local integration tests of the code."""

import logging
import argparse
from argparse import Namespace
from errors import NoTestCase
from read_data import validate_required_files, get_config
from events import run_global_reminder, run_personal_reminder

logging.basicConfig(level=logging.DEBUG)

# Disable this warning as the variable is not constant.
# Empty variable here to patch when testing.
# pylint: disable=C0103
args = None


def run_methods() -> None:
    """
    Test each event given in args.
    """
    for arg, value in vars(args).items():
        if value:
            call_method(arg)


def call_method(event: str) -> None:
    """
    Run the test logic for each event.
    :param event: The event to test
    """
    match event:
        case "channel":
            # Catch case for the required parameter "channel".
            # Nothing should run here as channel is an arg of other tests
            pass
        case "global":
            run_global_reminder(args.channel)
        case "personal":
            users = list(get_config("user-map").values())
            run_personal_reminder(users)
        case _:
            raise NoTestCase(f"There is not test case for {event}")


def main() -> None:
    """
    This function checks the config files, runs the tests then starts the application.
    """
    validate_required_files()
    logging.info("Running tests\n")
    run_methods()
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
