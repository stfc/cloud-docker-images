"""Unit tests for dev.py"""

from unittest.mock import patch
import pytest
from dev import run_tests, call_test, main, parse_args
from errors import NoTestCase


@patch("dev.argparse")
def test_parse_args(mock_argparse):
    """Test parse args"""
    mock_parser = mock_argparse.ArgumentParser.return_value
    res = parse_args()
    mock_argparse.ArgumentParser.assert_called_once()
    mock_parser.add_argument.assert_any_call(
        "channel", help="Channel to send messages to."
    )
    mock_parser.add_argument.assert_any_call(
        "--global", help="Test the global reminder", action="store_true"
    )
    mock_parser.add_argument.assert_any_call(
        "--personal", help="Test the personal reminder", action="store_true"
    )
    assert res == mock_argparse.ArgumentParser.return_value.parse_args.return_value


@patch("dev.validate_required_files")
@patch("dev.run_tests")
def test_main(mock_tests, mock_validate):
    """Test the main function."""
    main()
    mock_validate.assert_called_once()
    mock_tests.assert_called_once()


@patch("dev.args")
@patch("dev.run_personal_reminder")
@patch("dev.run_global_reminder")
def test_call_test(mock_global, mock_personal, mock_args):
    """Test the call test function"""
    call_test("global")
    mock_global.assert_called_once_with(mock_args.channel)
    call_test("personal")
    mock_personal.assert_called_once_with()
    with pytest.raises(NoTestCase) as exc:
        call_test("unexpected")
        assert str(exc.value) == "There is not test case for unexpected"


class MockArgs:
    """Mock class to patch global args with"""
    # Don't need public methods here as this is a class for mocking argparse
    # pylint: disable=R0903
    def __init__(self):
        """Mock argparse values"""
        self.global_test = True
        self.personal_test = True


@patch("dev.args", MockArgs())
@patch("dev.call_test")
def test_run_tests(mock_call_test):
    """Test that test calls are made."""
    run_tests()
    mock_call_test.assert_any_call("global_test")
    mock_call_test.assert_any_call("personal_test")
