"""Unit tests for events.slash_commands/slash_commands.py"""

from unittest.mock import patch, MagicMock

from helper.data import User
from events.slash_commands import (
    slash_prs,
    slash_mrs,
    slash_find_host,
)

# pylint: disable=R0801
MOCK_USER = User(
    real_name="mock user",
    github_name="mock_github",
    slack_id="mock_slack",
    gitlab_name="mock_gitlab",
)


@patch("events.slash_commands.filter_by")
@patch("events.slash_commands.FindPRsGitHub")
@patch("events.slash_commands.send_reminders")
@patch("events.slash_commands.get_config")
@patch("events.slash_commands.get_token")
def test_slash_prs_mine(
    mock_get_token, mock_get_config, mock_send_reminders, mock_find_prs, mock_filter_by
):
    """Test the function works when users choose "mine" """
    mock_get_config.side_effect = [[MOCK_USER], ["owner/repo"]]
    mock_filter_by.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": MOCK_USER.slack_id, "text": "mine"}
    mock_ack = MagicMock()
    slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_any_call("users")
    mock_get_config.assert_any_call("repos")
    mock_get_token.assert_called_once_with("GITHUB_TOKEN")
    mock_respond.assert_any_call("Finding the PRs...")
    mock_filter_by.assert_any_call([MOCK_USER], "slack_id", MOCK_USER.slack_id)
    mock_find_prs.return_value.run.assert_called_once_with(
        repos=["owner/repo"], token=mock_get_token.return_value
    )
    mock_filter_by.assert_any_call(
        obj_list=mock_find_prs.return_value.run.return_value,
        prop="author",
        value=MOCK_USER.github_name,
    )
    mock_send_reminders.assert_called_once_with(
        MOCK_USER.slack_id, mock_filter_by.return_value, True
    )


@patch("events.slash_commands.filter_by")
@patch("events.slash_commands.FindPRsGitHub")
@patch("events.slash_commands.send_reminders")
@patch("events.slash_commands.get_config")
@patch("events.slash_commands.get_token")
def test_slash_prs_all(
    mock_get_token, mock_get_config, mock_send_reminders, mock_find_prs, mock_filter_by
):
    """Test the function works when users choose "all" """
    mock_get_config.side_effect = [[MOCK_USER], ["owner/repo"]]
    mock_filter_by.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": MOCK_USER.slack_id, "text": "mine"}
    mock_ack = MagicMock()
    slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_any_call("users")
    mock_get_config.assert_any_call("repos")
    mock_get_token.assert_called_once_with("GITHUB_TOKEN")
    mock_respond.assert_any_call("Finding the PRs...")
    mock_filter_by.assert_any_call([MOCK_USER], "slack_id", MOCK_USER.slack_id)
    mock_find_prs.return_value.run.assert_called_once_with(
        repos=["owner/repo"], token=mock_get_token.return_value
    )
    mock_send_reminders.assert_called_once_with(
        MOCK_USER.slack_id, mock_filter_by.return_value, True
    )


@patch("events.slash_commands.get_config")
def test_slash_prs_fail(mock_get_config):
    """Test the function fails if no option is given"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": "mock_slack", "text": ""}
    mock_ack = MagicMock()
    slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call(
        "Please provide the correct argument: 'mine' or 'all'."
    )


@patch("events.slash_commands.get_config")
def test_slash_prs_no_user(mock_get_config):
    """Test the function fails if the user is not found in the config file"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": "non_existent_user", "text": ""}
    mock_ack = MagicMock()
    slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call(
        "Could not find your Slack ID non_existent_user in the user map. "
        "Please contact the service maintainer to fix this."
    )


@patch("events.slash_commands.filter_by")
@patch("events.slash_commands.FindPRsGitLab")
@patch("events.slash_commands.send_reminders")
@patch("events.slash_commands.get_config")
@patch("events.slash_commands.get_token")
def test_slash_mrs_mine(
    mock_get_token, mock_get_config, mock_send_reminders, mock_find_mrs, mock_filter_by
):
    """Test the function works when users choose "mine" """
    mock_get_config.side_effect = [[MOCK_USER], ["group&2Fproject"]]
    mock_filter_by.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": MOCK_USER.slack_id, "text": "mine"}
    mock_ack = MagicMock()
    slash_mrs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_any_call("users")
    mock_get_config.assert_any_call("projects")
    mock_get_token.assert_called_once_with("GITLAB_TOKEN")
    mock_respond.assert_any_call("Finding the MRs...")
    mock_filter_by.assert_any_call([MOCK_USER], "slack_id", MOCK_USER.slack_id)
    mock_find_mrs.return_value.run.assert_called_once_with(
        projects=["group&2Fproject"], token=mock_get_token.return_value
    )
    mock_filter_by.assert_any_call(
        obj_list=mock_find_mrs.return_value.run.return_value,
        prop="author",
        value=MOCK_USER.gitlab_name,
    )
    mock_send_reminders.assert_called_once_with(
        MOCK_USER.slack_id, mock_filter_by.return_value, True
    )


@patch("events.slash_commands.filter_by")
@patch("events.slash_commands.FindPRsGitLab")
@patch("events.slash_commands.send_reminders")
@patch("events.slash_commands.get_config")
@patch("events.slash_commands.get_token")
def test_slash_mrs_all(
    mock_get_token, mock_get_config, mock_send_reminders, mock_find_mrs, mock_filter_by
):
    """Test the function works when users choose "all" """
    mock_get_config.side_effect = [[MOCK_USER], ["group&2Fproject"]]
    mock_filter_by.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": MOCK_USER.slack_id, "text": "all"}
    mock_ack = MagicMock()
    slash_mrs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_any_call("users")
    mock_get_config.assert_any_call("projects")
    mock_get_token.assert_called_once_with("GITLAB_TOKEN")
    mock_respond.assert_any_call("Finding the MRs...")
    mock_filter_by.assert_any_call([MOCK_USER], "slack_id", MOCK_USER.slack_id)
    mock_find_mrs.return_value.run.assert_called_once_with(
        projects=["group&2Fproject"], token=mock_get_token.return_value
    )
    mock_send_reminders.assert_called_once_with(
        MOCK_USER.slack_id, mock_find_mrs.return_value.run.return_value, True
    )


@patch("events.slash_commands.get_config")
def test_slash_mrs_fail(mock_get_config):
    """Test the function fails if no option is given"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": "mock_slack", "text": ""}
    mock_ack = MagicMock()
    slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call(
        "Please provide the correct argument: 'mine' or 'all'."
    )


@patch("events.slash_commands.get_config")
def test_slash_mrs_no_user(mock_get_config):
    """Test the function fails if the user is not found in the config file"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = MagicMock()
    mock_command = {"user_id": "non_existent_user", "text": ""}
    mock_ack = MagicMock()
    slash_mrs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call(
        "Could not find your Slack ID non_existent_user in the user map. "
        "Please contact the service maintainer to fix this."
    )
