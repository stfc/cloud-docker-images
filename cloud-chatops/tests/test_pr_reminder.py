"""Tests for pr_reminder.py"""
from dataclasses import replace
from datetime import datetime

import pytest
from unittest.mock import patch, NonCallableMock, MagicMock

from slack_sdk.errors import SlackApiError

from features.pr_reminder import PRReminder
from pr_dataclass import PR, Message


@pytest.fixture(name="instance", scope="function")
def instance_fixture():
    return PRReminder(NonCallableMock())


MOCK_PR = PR(
    title="mock_title #1",
    author="mock_author",
    url="https://api.github.com/repos/mock_owner/mock_repo/pulls",
    stale=True,
    draft=True,
    labels=["mock_label"],
    repository="mock_repo",
    created_at=datetime.strptime("2024-11-15T07:33:56Z", "%Y-%m-%dT%H:%M:%SZ"),
)


def test_get_reactions(instance):
    """Test reactions are returned."""
    res = instance.get_reactions(MOCK_PR)
    assert res == ["alarm_clock", "building_construction"]


def test_get_reactions_none(instance):
    """Test no reactions are returned."""
    mock_pr = replace(MOCK_PR, draft=False, stale=False)
    res = instance.get_reactions(mock_pr)
    assert not res


@patch("features.pr_reminder.get_config")
def test_make_string(mock_get_config, instance):
    """Test the right string is returned."""
    mock_get_config.return_value = {"mock_author": "mock_slack"}
    instance.client.users_profile_get.return_value = {"profile":{"real_name":"mock_real_name"}}
    res = instance.make_string(MOCK_PR)
    mock_get_config.assert_called_once_with("user-map")
    instance.client.users_profile_get.assert_called_once_with(user="mock_slack")
    expected = f"*This PR is older than 30 days. Consider closing it:*\nPull Request: <{MOCK_PR.url}|{MOCK_PR.title}>\nAuthor: mock_real_name"
    assert res == expected


@patch("features.pr_reminder.get_config")
def test_make_string_fails(mock_get_config, instance):
    """Test the github name is used if slack name can't be found."""
    instance.client.users_profile_get.side_effect = SlackApiError("mock", "mock")
    mock_get_config.return_value.get.return_value = "mock_author"
    res = instance.make_string(MOCK_PR)
    expected = f"*This PR is older than 30 days. Consider closing it:*\nPull Request: <{MOCK_PR.url}|{MOCK_PR.title}>\nAuthor: mock_author"
    assert res == expected


@patch("features.pr_reminder.PRReminder.make_string")
@patch("features.pr_reminder.PRReminder.get_reactions")
def test_construct_messages(mock_get_reactions, mock_make_string, instance):
    """Test the correct messages are returned"""
    mock_make_string.return_value = "mock_string"
    mock_get_reactions.return_value = ["mock_reaction"]
    res = instance.construct_messages([MOCK_PR])
    assert res == [Message(text="mock_string", reactions=["mock_reaction"])]


def test_add_reactions(instance):
    """Test reaction add calls are made."""
    instance.client.reactions_add.return_value = {"ok": True}
    instance.add_reactions("mock_timestamp", "mock_channel", ["mock_reaction"])
    instance.client.reactions_add.assert_called_once_with(channel="mock_channel", name="mock_reaction", timestamp="mock_timestamp")


def test_add_reactions_fails(instance):
    """Test reaction add calls are made and fail."""
    instance.client.reactions_add.return_value = {"ok": False, "error": "mock_error"}
    with pytest.raises(RuntimeError) as exc:
        instance.add_reactions("mock_timestamp", "mock_channel", ["mock_reaction"])
        assert str(exc.value) == 'Reaction failed to add with error: mock_error'


@patch("features.pr_reminder.PRReminder.add_reactions")
def test_send_message(mock_add_reactions, instance):
    """Test the chat post message is called with the correct parameters"""
    mock_response = MagicMock()
    mock_response["ok"] = True
    mock_response.data = {"ts": "mock_timestamp"}
    instance.client.chat_postMessage.return_value = mock_response

    res = instance.send_message("mock_text", "mock_channel", ["mock_reaction"], "mock_timestamp")
    instance.client.chat_postMessage.assert_called_once_with(text="mock_text", channel="mock_channel", unfurl_links=False, thread_ts="mock_timestamp")
    mock_add_reactions.assert_called_once_with("mock_timestamp", "mock_channel", ["mock_reaction"])
    assert res == mock_response


@patch("features.pr_reminder.PRReminder.add_reactions")
def test_send_message_fails(_, instance):
    """Test an exception is raised if the message fails to send."""
    mock_response = MagicMock()
    mock_response["ok"] = False
    mock_response["error"] = "mock_error"
    mock_response.data = {"ts": "mock_timestamp"}
    instance.client.chat_postMessage.return_value = mock_response
    with pytest.raises(RuntimeError) as exc:
        instance.send_message("mock_text", "mock_channel", ["mock_reaction"], "mock_timestamp")
        # assert str(exc.value) == 'Message failed to send with error: mock_error'
