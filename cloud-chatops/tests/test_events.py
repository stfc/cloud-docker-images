"""Unit tests for events.py"""

from unittest.mock import patch, AsyncMock
import pytest

from data import User
from events import (
    run_global_reminder,
    run_personal_reminder,
    schedule_jobs,
    slash_prs,
    slash_find_host,
)

MOCK_USER = User(
    real_name="mock user", github_name="mock_github", slack_id="mock_slack"
)


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
        repos=mock_get_config.return_value
    )
    mock_find_prs.return_value.sort_by.assert_called_once_with(
        mock_find_prs.return_value.run.return_value, "created_at", False
    )
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_find_prs.return_value.sort_by.return_value, channel="mock_channel"
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
    mock_get_config.side_effect = [mock_repos]
    run_personal_reminder([MOCK_USER])
    mock_find_prs.return_value.run.assert_called_once_with(repos=mock_repos)
    mock_find_prs.return_value.sort_by.assert_called_once_with(
        mock_find_prs.return_value.run.return_value, "created_at", False
    )
    mock_find_prs.return_value.filter_by.assert_called_once_with(
        mock_find_prs.return_value.sort_by.return_value, "author", "mock_github"
    )
    mock_get_config.assert_any_call("repos")
    mock_web_client.assert_called_once_with(token=mock_get_token.return_value)
    mock_get_token.assert_called_once_with("SLACK_BOT_TOKEN")
    mock_pr_reminder.assert_called_once_with(mock_web_client.return_value)
    mock_pr_reminder.return_value.run.assert_called_once_with(
        prs=mock_find_prs.return_value.filter_by.return_value,
        channel="mock_slack",
        message_no_prs=False,
    )


@pytest.mark.asyncio
@patch("events.schedule")
@patch("events.get_config")
async def test_schedule_jobs(mock_get_config, mock_schedule):
    """Test the correct jobs are scheduled"""
    mock_get_config.side_effect = ["channel", [MOCK_USER]]
    # Force an exception then catch it here.
    # This is to prevent the test entering the infinite while wait loop.
    mock_schedule.run_pending.side_effect = Exception()
    with pytest.raises(Exception):
        await schedule_jobs()
    mock_get_config.assert_any_call("users")
    mock_get_config.assert_any_call("channel")
    mock_schedule.every.return_value.monday.at.assert_any_call("09:00")
    mock_schedule.every.return_value.monday.at.return_value.do.assert_any_call(
        run_global_reminder, channel="channel"
    )
    mock_schedule.every.return_value.monday.at.return_value.do.assert_any_call(
        run_personal_reminder, users=[MOCK_USER]
    )
    mock_schedule.every.return_value.wednesday.at.assert_any_call("09:00")
    mock_schedule.every.return_value.wednesday.at.return_value.do.assert_any_call(
        run_global_reminder, channel="channel"
    )
    mock_schedule.run_pending.assert_called_once_with()


@pytest.mark.asyncio
@patch("events.run_personal_reminder")
@patch("events.get_config")
async def test_slash_prs_mine(mock_get_config, mock_run_personal):
    """Test the function works when users choose mine"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = AsyncMock()
    mock_command = {"user_id": "mock_slack", "text": "mine"}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call("Gathering the PRs...")
    mock_respond.assert_any_call("Check out your DMs.")
    mock_run_personal.assert_called_once_with([MOCK_USER], message_no_prs=True)


@pytest.mark.asyncio
@patch("events.run_global_reminder")
@patch("events.get_config")
async def test_slash_prs_all(mock_get_config, mock_run_global):
    """Test the function works when users choose all"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = AsyncMock()
    mock_command = {"user_id": "mock_slack", "text": "all"}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call("Gathering the PRs...")
    mock_respond.assert_any_call("Check out your DMs.")
    mock_run_global.assert_called_once_with("mock_slack")


@pytest.mark.asyncio
@patch("events.get_config")
async def test_slash_prs_fail(mock_get_config):
    """Test the function fails if no option is given"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = AsyncMock()
    mock_command = {"user_id": "mock_slack", "text": ""}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call(
        "Please provide the correct argument: 'mine' or 'all'."
    )


@pytest.mark.asyncio
@patch("events.get_config")
async def test_slash_prs_no_user(mock_get_config):
    """Test the function fails if the user is not found in the config file"""
    mock_get_config.return_value = [MOCK_USER]
    mock_respond = AsyncMock()
    mock_command = {"user_id": "non_existent_user", "text": ""}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("users")
    mock_respond.assert_any_call(
        "Could not find your Slack ID non_existent_user in the user map. "
        "Please contact the service maintainer to fix this."
    )


@pytest.mark.asyncio
@patch("events.os")
async def test_slash_find_host(mock_os):
    """Test that the environment variable is retrieved and responded."""
    mock_ack = AsyncMock()
    mock_respond = AsyncMock()
    await slash_find_host(mock_ack, mock_respond)
    mock_ack.assert_called_once_with()
    mock_os.environ.get.assert_called_once_with("HOST_IP")
    mock_respond.assert_called_once_with(
        f"The host IP of this node is: {mock_os.environ.get.return_value}"
    )
