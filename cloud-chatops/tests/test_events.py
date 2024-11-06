"""Unit tests for events.py"""

from unittest.mock import patch
from events import run_global_reminder, run_personal_reminder


@patch("events.PostPRsToSlack")
def test_run_global_reminder(mock_post_prs_to_slack):
    """Test global reminder event"""
    run_global_reminder("mock_channel")
    mock_post_prs_to_slack.return_value.run.assert_called_once_with(
        channel="mock_channel"
    )


@patch("events.get_config")
@patch("events.PostToDMs")
def test_run_personal_reminder(mock_post_to_dms, mock_config):
    """Test personal reminder event"""
    mock_config.return_value = {"mock_github_name": "mock_slack_name"}
    run_personal_reminder()
    mock_post_to_dms.return_value.run.assert_called_once_with(
        users=["mock_slack_name"], post_all=False
    )
