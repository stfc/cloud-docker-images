"""Unit tests for events/weekly_reminders.py"""

from unittest.mock import patch
import pytest

from helper.data import User
from events.weekly_reminders import (
    run_global_reminder,
    run_personal_reminder,
    weekly_reminder,
)

MOCK_USER = User(
    real_name="mock user", github_name="mock_github", slack_id="mock_slack"
)

# Disable for patching
# pylint: disable=R0917
# pylint: disable=R0913


@patch("events.weekly_reminders.sort_by")
@patch("events.weekly_reminders.WebClient")
@patch("events.weekly_reminders.get_token")
@patch("events.weekly_reminders.get_config")
@patch("events.weekly_reminders.FindPRsGitHub")
@patch("events.weekly_reminders.PRReminder")
def test_run_global_reminder(
    mock_pr_reminder,
    mock_find_prs,
    mock_get_config,
    mock_get_token,
    mock_web_client,
    mock_sort_by,
):
    """Test global reminder event"""
    mock_get_token.side_effect = ["mock_github", "mock_slack"]
    run_global_reminder("mock_channel")
    mock_find_prs.return_value.run.assert_called_once_with(
        repos=mock_get_config.return_value, token="mock_github"
    )
    mock_sort_by.assert_called_once_with(
        mock_find_prs.return_value.run.return_value, "created_at", False
    )
    mock_web_client.assert_called_once_with(token="mock_slack")
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_sort_by.return_value, channel="mock_channel"
    )
    mock_get_config.assert_called_once_with("repos")
    mock_get_token.assert_any_call("GITHUB_TOKEN")
    mock_get_token.assert_any_call("SLACK_BOT_TOKEN")


# Disable for patching
# pylint: disable=R0917
# pylint: disable=R0913


@patch("events.weekly_reminders.sort_by")
@patch("events.weekly_reminders.filter_by")
@patch("events.weekly_reminders.WebClient")
@patch("events.weekly_reminders.get_token")
@patch("events.weekly_reminders.get_config")
@patch("events.weekly_reminders.FindPRsGitHub")
@patch("events.weekly_reminders.PRReminder")
def test_run_personal_reminder(
    mock_pr_reminder,
    mock_find_prs,
    mock_get_config,
    mock_get_token,
    mock_web_client,
    mock_filter_by,
    mock_sort_by,
):
    """Test personal reminder event"""
    mock_get_token.side_effect = ["mock_github", "mock_slack"]
    mock_repos = {"mock_owner": ["mock_repo"]}
    mock_get_config.side_effect = [mock_repos]
    run_personal_reminder([MOCK_USER])
    mock_find_prs.return_value.run.assert_called_once_with(
        repos=mock_repos, token="mock_github"
    )
    mock_sort_by.assert_called_once_with(
        mock_find_prs.return_value.run.return_value, "created_at", False
    )
    mock_filter_by.assert_called_once_with(
        mock_sort_by.return_value, "author", "mock_github"
    )
    mock_get_config.assert_any_call("repos")
    mock_web_client.assert_called_once_with(token="mock_slack")
    mock_get_token.assert_any_call("SLACK_BOT_TOKEN")
    mock_get_token.assert_any_call("GITHUB_TOKEN")
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_filter_by.return_value,
        channel="mock_slack",
        message_no_prs=False,
    )


@patch("events.weekly_reminders.run_global_reminder")
@patch("events.weekly_reminders.run_personal_reminder")
@patch("events.weekly_reminders.get_config")
def test_weekly_reminder(mock_get_config, mock_personal, mock_global):
    """Test the correct jobs are run"""
    mock_get_config.side_effect = ["channel", [MOCK_USER]]
    weekly_reminder("global")
    mock_get_config.assert_any_call("channel")
    mock_global.assert_called_once_with("channel")

    weekly_reminder("personal")
    mock_get_config.assert_any_call("users")
    mock_personal.assert_called_once_with(users=[MOCK_USER], message_no_prs=False)


def test_weekly_reminder_fails():
    """Test the functions raises an error for an incorrect job."""
    with pytest.raises(ValueError):
        weekly_reminder("some_incorrect_value")



