"""Unit tests for events.py"""

from unittest.mock import patch, AsyncMock
import pytest
from events import run_global_reminder, run_personal_reminder, schedule_jobs, slash_prs
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


@pytest.mark.asyncio
@patch("events.schedule")
@patch("events.get_config")
async def test_schedule_jobs(mock_get_config, mock_schedule):
    """Test the correct jobs are scheduled"""
    mock_get_config.return_value = {"mock_github": "mock_slack"}
    mock_schedule.run_pending.side_effect = Exception()
    with pytest.raises(Exception):
        await schedule_jobs()
    mock_get_config.assert_called_once_with("user-map")
    mock_schedule.every.return_value.monday.at.assert_any_call("09:00")
    mock_schedule.every.return_value.monday.at.return_value.do.assert_any_call(
        run_global_reminder, channel="C03RT2F6WHZ"
    )
    mock_schedule.every.return_value.monday.at.return_value.do.assert_any_call(
        run_personal_reminder, users=["mock_slack"]
    )
    mock_schedule.every.return_value.wednesday.at.assert_any_call("09:00")
    mock_schedule.every.return_value.wednesday.at.return_value.do.assert_any_call(
        run_global_reminder, channel="C03RT2F6WHZ"
    )
    mock_schedule.run_pending.assert_called_once_with()


@pytest.mark.asyncio
@patch("events.run_personal_reminder")
@patch("events.get_config")
async def test_slash_prs_mine(mock_get_config, mock_run_personal):
    """Test the function calls the correct methods for different inputs"""
    mock_get_config.return_value = {"mock_github": "mock_user_id"}
    mock_respond = AsyncMock()
    mock_command = {"user_id": "mock_user_id", "text": "mine"}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("user-map")
    mock_respond.assert_any_call("Gathering the PRs...")
    mock_respond.assert_any_call("Check out your DMs.")
    mock_run_personal.assert_called_once_with(["mock_user_id"])


@pytest.mark.asyncio
@patch("events.run_global_reminder")
@patch("events.get_config")
async def test_slash_prs_all(mock_get_config, mock_run_global):
    """Test the function calls the correct methods for different inputs"""
    mock_get_config.return_value = {"mock_github": "mock_user_id"}
    mock_respond = AsyncMock()
    mock_command = {"user_id": "mock_user_id", "text": "all"}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("user-map")
    mock_respond.assert_any_call("Gathering the PRs...")
    mock_respond.assert_any_call("Check out your DMs.")
    mock_run_global.assert_called_once_with("mock_user_id")


@pytest.mark.asyncio
@patch("events.get_config")
async def test_slash_prs_fail(mock_get_config):
    """Test the function calls the correct methods for different inputs"""
    mock_get_config.return_value = {"mock_github": "mock_user_id"}
    mock_respond = AsyncMock()
    mock_command = {"user_id": "mock_user_id", "text": ""}
    mock_ack = AsyncMock()
    await slash_prs(mock_ack, mock_respond, mock_command)
    mock_ack.assert_called_once_with()
    mock_get_config.assert_called_once_with("user-map")
    mock_respond.assert_any_call(
        "Please provide the correct argument: 'mine' or 'all'."
    )
