"""Unit tests for events.slash_commands/slash_prs.py"""

from unittest.mock import patch, MagicMock
from datetime import datetime

import pytest
from helper.data import User, PR
from events.slash_prs import SlashPRs

# pylint: disable=R0801
MOCK_USER = User(
    real_name="mock user",
    github_name="mock_author",
    slack_id="mock_slack",
    gitlab_name="mock_author",
)

# pylint: disable=R0801
MOCK_PR = PR(
    title="mock_title #1",
    author="mock_author",
    url="https://api.github.com/repos/mock_owner/mock_repo/pulls",
    stale=True,
    draft=False,
    labels=["mock_label"],
    repository="mock_repo",
    created_at=datetime.strptime("2024-11-15T07:33:56Z", "%Y-%m-%dT%H:%M:%SZ"),
)


@pytest.fixture(name="instance")
def fixture_instance():
    """Create a class instance for testing."""
    return SlashPRs()


@patch("events.slash_prs.get_config")
def test_run_invalid_features(mock_get_config, instance):
    """Test an error is raised when no features are enabled in the config."""
    mock_get_config.side_effect = [[MOCK_USER], {"enabled": False}, {"enabled": False}]
    mock_respond = MagicMock()
    with pytest.raises(RuntimeError) as exc:
        instance.run(MagicMock(), mock_respond, {})
    mock_respond.assert_called_once_with(
        "Neither of the GitHub or GitLab features are enabled."
    )
    assert str(exc.value) == (
        "Neither the GitHub or GitLab features are enabled."
        " At least one of these needs to be enabled to function."
    )


@patch("events.slash_prs.get_config")
def test_run_invalid_user(mock_get_config, instance):
    """Test an error is raised when the given user is not in the config."""
    mock_get_config.side_effect = [[MOCK_USER], {"enabled": True}, {"enabled": True}]
    mock_respond = MagicMock()
    with pytest.raises(RuntimeError) as exc:
        instance.run(MagicMock(), mock_respond, {"user_id": "some_unknown_user"})
    mock_respond.assert_called_once_with(
        f"Could not find your Slack ID some_unknown_user in the user map. "
        f"Please contact the service maintainer to fix this."
    )
    assert (
        str(exc.value)
        == "User with Slack ID some_unknown_user tried using /prs but is not listed in the config."
    )


@patch("events.slash_prs.get_config")
def test_run_invalid_arguments(mock_get_config, instance):
    """Test an error is raised when the given arguments are not valid."""
    mock_get_config.side_effect = [[MOCK_USER], {"enabled": True}, {"enabled": True}]
    mock_respond = MagicMock()
    with pytest.raises(RuntimeError) as exc:
        instance.run(
            MagicMock(), mock_respond, {"user_id": "mock_slack", "text": "invalid_arg"}
        )
    mock_respond.assert_called_once_with(
        "Please provide the correct argument: 'mine' or 'all'."
    )
    assert str(exc.value) == (
        "User tried to run /prs with arguments invalid_arg."
        " Failed as arguments provided are not valid."
    )


@patch("events.slash_prs.send_reminders")
@patch("events.slash_prs.FindPRsGitHub")
@patch("events.slash_prs.FindPRsGitLab")
@patch("events.slash_prs.get_token")
@patch("events.slash_prs.get_config")
def test_run(
    mock_get_config,
    mock_get_token,
    mock_gitlab,
    mock_github,
    mock_send_reminders,
    instance,
):
    """Test the run method makes the correct calls."""
    mock_get_config.side_effect = [
        [MOCK_USER],
        {"enabled": True},
        {"enabled": True},
        {"enabled": True},
        {"enabled": True},
        ["mock_owner/mock_repo"],
        {"enabled": True},
        ["mock_group%2Fmock_project"],
    ]
    mock_get_token.side_effect = ["mock_github_token", "mock_gitlab_token"]
    mock_respond = MagicMock()
    mock_gitlab.return_value.run.return_value = [MOCK_PR]
    mock_github.return_value.run.return_value = [MOCK_PR]

    instance.run(MagicMock(), mock_respond, {"user_id": "mock_slack", "text": "mine"})
    mock_respond.assert_called_once_with("Finding the PRs...")
    mock_send_reminders.assert_called_once_with("mock_slack", [MOCK_PR, MOCK_PR], True)
    for call in ["users", "github", "gitlab", "repos", "projects"]:
        mock_get_config.assert_any_call(call)
    for call in ["GITHUB_TOKEN", "GITLAB_TOKEN"]:
        mock_get_token.assert_any_call(call)
