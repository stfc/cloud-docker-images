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
    real_name="mock user",
    github_name="mock_github",
    slack_id="mock_slack",
    gitlab_name="mock_gitlab",
)


# Disable for patching
# pylint: disable=R0917
# pylint: disable=R0913
@patch("events.weekly_reminders.sort_by")
@patch("events.weekly_reminders.WebClient")
@patch("events.weekly_reminders.get_secrets")
@patch("events.weekly_reminders.get_config")
@patch("events.weekly_reminders.FindPRsGitLab")
@patch("events.weekly_reminders.FindPRsGitHub")
@patch("events.weekly_reminders.PRReminder")
def test_run_global_reminder(
    mock_slack,
    mock_find_prs_gh,
    mock_find_prs_gl,
    mock_get_config,
    mock_get_secrets,
    mock_web_client,
    mock_sort_by,
):
    """Test global reminder event"""
    mock_config = mock_get_config.return_value
    mock_secrets = mock_get_secrets.return_value
    mock_config.github.enabled = True
    mock_config.gitlab.enabled = True
    run_global_reminder("mock_channel")

    mock_find_prs_gh.return_value.run.assert_called_once_with(
        repos=mock_config.github.repositories, token=mock_secrets.GITHUB_TOKEN
    )
    mock_find_prs_gl.return_value.run.assert_called_once_with(
        projects=mock_config.gitlab.projects, token=mock_secrets.GITLAB_TOKEN
    )
    unsorted_prs = []
    unsorted_prs += mock_find_prs_gh.return_value.run.return_value
    unsorted_prs += mock_find_prs_gl.return_value.run.return_value
    mock_sort_by.assert_called_once_with(unsorted_prs, "created_at", False)
    mock_web_client.assert_called_once_with(token=mock_secrets.SLACK_BOT_TOKEN)
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_sort_by.return_value, channel="mock_channel"
    )


# Disable for patching
# pylint: disable=R0917
# pylint: disable=R0913
@patch("events.weekly_reminders.sort_by")
@patch("events.weekly_reminders.filter_by")
@patch("events.weekly_reminders.WebClient")
@patch("events.weekly_reminders.get_secrets")
@patch("events.weekly_reminders.get_config")
@patch("events.weekly_reminders.FindPRsGitLab")
@patch("events.weekly_reminders.FindPRsGitHub")
@patch("events.weekly_reminders.PRReminder")
def test_run_personal_reminder(
    mock_slack,
    mock_find_prs_gh,
    mock_find_prs_gl,
    mock_get_config,
    mock_get_secrets,
    mock_web_client,
    mock_filter_by,
    mock_sort_by,
):
    """Test personal reminder event"""
    mock_config = mock_get_config.return_value
    mock_secrets = mock_get_secrets.return_value
    mock_config.github.enabled = True
    mock_config.gitlab.enabled = True

    run_personal_reminder([MOCK_USER])
    mock_find_prs_gh.return_value.run.assert_called_once_with(
        repos=mock_config.github.repositories, token=mock_secrets.GITHUB_TOKEN
    )
    mock_find_prs_gl.return_value.run.assert_called_once_with(
        projects=mock_config.gitlab.projects, token=mock_secrets.GITLAB_TOKEN
    )
    unsorted_prs = []
    unsorted_prs += mock_find_prs_gh.return_value.run.return_value
    unsorted_prs += mock_find_prs_gl.return_value.run.return_value
    mock_sort_by.assert_called_once_with(unsorted_prs, "created_at", False)
    mock_filter_by.assert_called_once_with(
        mock_sort_by.return_value,
        "author",
        [MOCK_USER.github_name, MOCK_USER.gitlab_name],
    )
    mock_web_client.assert_called_once_with(token=mock_secrets.SLACK_BOT_TOKEN)
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_filter_by.return_value,
        channel=MOCK_USER.slack_id,
        message_no_prs=False,
    )


@patch("events.weekly_reminders.run_global_reminder")
@patch("events.weekly_reminders.run_personal_reminder")
@patch("events.weekly_reminders.get_config")
def test_weekly_reminder(mock_get_config, mock_personal, mock_global):
    """Test the correct jobs are run"""
    mock_get_config.return_value.users = [MOCK_USER]
    weekly_reminder({"reminder_type": "global", "channel": "mock_channel"})
    mock_global.assert_called_once_with("mock_channel")

    weekly_reminder({"reminder_type": "personal"})
    mock_personal.assert_called_once_with(users=[MOCK_USER], message_no_prs=False)


@patch("events.weekly_reminders.get_config")
def test_weekly_reminder_fails_unknown_type(_):
    """Test the functions raises an error for an incorrect job."""
    with pytest.raises(ValueError):
        weekly_reminder({"reminder_type": "unknown_value"})


@patch("events.weekly_reminders.get_config")
def test_weekly_reminder_fails_no_channel(_):
    """Test the functions raises an error for not having a channel value."""
    with pytest.raises(ValueError):
        weekly_reminder({"reminder_type": "global"})
