"""Unit tests for dev.py"""

from unittest.mock import patch, NonCallableMock, MagicMock
import pytest
from helper.data import User
from helper.exceptions import NoTestCase
from helper.config import Secrets
from dev import run_methods, call_method, parse_args, main

# pylint: disable=R0801
MOCK_USER = User(
    real_name="mock user",
    github_name="mock_github",
    slack_id="mock_slack",
    gitlab_name="mock_gitlab",
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


mock_config = MagicMock()


@patch("dev.CONFIG", mock_config)
@patch("dev.run_personal_reminder")
@patch("dev.run_global_reminder")
def test_call_test(mock_global, mock_personal):
    """Test the call test function"""
    mock_args = NonCallableMock()
    call_method("channel", mock_args)
    call_method("global", mock_args)
    mock_global.assert_called_once_with(mock_args.channel)
    call_method("personal", mock_args)
    mock_personal.assert_called_once_with(mock_config.users)
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


mock_secrets = Secrets(
    SLACK_BOT_TOKEN="mock_slack_bot_token", SLACK_APP_TOKEN="mock_slack_app_token"
)


@patch("dev.SECRETS", mock_secrets)
@patch("dev.SocketModeHandler")
@patch("dev.App")
@patch("dev.run_methods")
def test_main(mock_run_methods, mock_app, mock_socket):
    """Test the main method calls the correct functions."""
    mock_args = NonCallableMock()
    main(mock_args)
    mock_run_methods.assert_called_once_with(mock_args)
    mock_app.assert_called_once_with(token="mock_slack_bot_token")
    mock_socket.assert_called_once_with(mock_app.return_value, "mock_slack_app_token")
    mock_socket.return_value.start.assert_called_once_with()
