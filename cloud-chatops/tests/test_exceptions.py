"""Tests for helper.exceptions"""

from helper.exceptions import ErrorInSecrets, ErrorInConfig
import pytest


def test_error_in_config():
    """Test the error raises the right message."""
    with pytest.raises(ErrorInConfig) as exc_info:
        raise ErrorInConfig("github", "enabled")
    assert exc_info.value.args[0] == (
        "There is a problem with your config.yaml."
        " The feature github does not have the parameter enabled set."
    )


def test_error_in_secrets():
    """Test the error raises the right message."""
    with pytest.raises(ErrorInSecrets) as exc_info:
        raise ErrorInSecrets("SLACK_BOT_TOKEN")
    assert (
        exc_info.value.args[0]
        == "There is a problem with your secrets.yaml. The secret SLACK_BOT_TOKEN is not set."
    )
