"""Unit tests for dev.py"""

from unittest.mock import patch, NonCallableMock
import pytest
from dev import run_methods, call_method, parse_args
from errors import NoTestCase


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


@patch("dev.validate_required_files")
@patch("dev.run_methods")
def test_main(mock_methods, mock_validate):
    """Test the main function."""
    main()
    mock_validate.assert_called_once()
    mock_methods.assert_called_once()


@patch("dev.args")
@patch("dev.get_config")
@patch("dev.run_personal_reminder")
@patch("dev.run_global_reminder")
def test_call_test(mock_global, mock_personal, mock_get_config, mock_args):
    """Test the call test function"""
    mock_get_config.return_value = {"mock_github": "mock_slack"}
    call_method("channel")
    call_method("global")
    mock_global.assert_called_once_with(mock_args.channel)
    call_method("personal")
    mock_personal.assert_called_once_with(["mock_slack"])
    with pytest.raises(NoTestCase) as exc:
        call_method("unexpected", mock_args)
        assert str(exc.value) == "There is not test case for unexpected"


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
    with pytest.raises(ValueError) as exc:
        run_methods(mock_args)
        assert str(exc.value) == "If using --global then --channel is required"
