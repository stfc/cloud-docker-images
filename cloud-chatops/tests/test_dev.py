"""Unit tests for dev.py"""

from unittest.mock import patch, NonCallableMock
import pytest

from helper.data import User
from dev import run_methods, call_method, parse_args
from helper.errors import NoTestCase


MOCK_USER = User(
    real_name="mock user", github_name="mock_github", slack_id="mock_slack"
)


@patch("dev.argparse")
def test_parse_args(mock_argparse):
    """Test parse args"""
    mock_parser = mock_argparse.ArgumentParser.return_value
    res = parse_args()
    mock_argparse.ArgumentParser.assert_called_once()
    mock_parser.add_argument.assert_any_call(
        "--channel", help="Channel to send messages to."
    )
    mock_parser.add_argument.assert_any_call(
        "--global", help="Test the global reminder", action="store_true"
    )
    mock_parser.add_argument.assert_any_call(
        "--personal", help="Test the personal reminder", action="store_true"
    )
    assert res == mock_argparse.ArgumentParser.return_value.parse_args.return_value


@patch("dev.get_config")
@patch("dev.run_personal_reminder")
@patch("dev.run_global_reminder")
def test_call_test(mock_global, mock_personal, mock_get_config):
    """Test the call test function"""
    mock_get_config.return_value = [MOCK_USER]
    mock_args = NonCallableMock()
    call_method("channel", mock_args)
    call_method("global", mock_args)
    mock_global.assert_called_once_with(mock_args.channel)
    call_method("personal", mock_args)
    mock_personal.assert_called_once_with([MOCK_USER])
    with pytest.raises(NoTestCase):
        call_method("unexpected", mock_args)


@patch("dev.call_method")
def test_run_methods(mock_call_method):
    """Test that test calls are made."""
    mock_args = NonCallableMock()
    mock_args.personal = True
    mock_args.channel = "mock_channel"
    setattr(mock_args, "global", True)
    run_methods(mock_args)
    mock_call_method.assert_any_call("global", mock_args)
    mock_call_method.assert_any_call("personal", mock_args)
    mock_call_method.assert_any_call("channel", mock_args)


def test_run_methods_invalid():
    """Test an error is raised when --global is supplied without --channel."""
    mock_args = NonCallableMock()
    setattr(mock_args, "global", True)
    mock_args.channel = ""
    with pytest.raises(ValueError):
        run_methods(mock_args)
