"""Unit tests for events.py"""

from unittest.mock import patch
from events import run_global_reminder, run_personal_reminder
from pr_dataclass import PRProps


@patch("events.WebClient")
@patch("events.get_token")
@patch("events.get_config")
@patch("events.FindPRs")
@patch("events.PRReminder")
def test_run_global_reminder(
    mock_pr_reminder, mock_find_prs, mock_get_config, mock_get_token, mock_web_client
):
    """Test global reminder event"""
    run_global_reminder("mock_channel")
    mock_find_prs.return_value.run.assert_called_once_with(
        repos=mock_get_config.return_value, sort=(PRProps.CREATED_AT, False)
    )
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_find_prs.return_value.run.return_value, channel="mock_channel"
    )
    mock_get_config.assert_called_once_with("repos")
    mock_get_token.assert_called_once_with("SLACK_BOT_TOKEN")


@patch("events.WebClient")
@patch("events.get_token")
@patch("events.get_config")
@patch("events.FindPRs")
@patch("events.PRReminder")
def test_run_personal_reminder(
    mock_pr_reminder, mock_find_prs, mock_get_config, mock_get_token, mock_web_client
):
    """Test personal reminder event"""
    mock_repos = {"mock_owner": ["mock_repo"]}
    mock_get_config.side_effect = [mock_repos, {"mock_github": "mock_slack"}]
    run_personal_reminder(["mock_slack"])
    mock_find_prs.assert_called_once()
    mock_find_prs.return_value.run.assert_called_once_with(
        repos=mock_repos, sort=(PRProps.CREATED_AT, False)
    )
    mock_get_config.assert_any_call("repos")
    mock_get_config.assert_any_call("user-map")
    mock_web_client.assert_called_once_with(token=mock_get_token.return_value)
    mock_get_token.assert_called_once_with("SLACK_BOT_TOKEN")
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_find_prs.return_value.run.return_value,
        channel="mock_slack",
        filter_by=(PRProps.AUTHOR, "mock_github"),
        message_no_prs=False,
    )
