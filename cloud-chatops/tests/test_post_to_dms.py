"""Unit tests for post_to_dms.py"""

from unittest.mock import NonCallableMock, patch
import pytest
from enum_states import PRsFoundState
from errors import NoUsersGiven
from features.post_to_dms import PostToDMs

# Disabling access to protected methods.
# pylint: disable=W0212


@pytest.fixture(name="instance", scope="function")
@patch("features.post_to_dms.PRMessageBuilder")
@patch("features.base_feature.WebClient")
@patch("features.base_feature.FindPRs")
@patch("features.base_feature.get_token")
@patch("features.base_feature.get_config")
def instance_fixture(
    _,
    mock_get_token,
    mock_find_prs,
    mock_web_client,
    mock_pr_message_builder,
):
    """This fixture provides a class instance for the tests"""
    mock_get_token.return_value = "mock_slack_token"
    mock_find_prs.return_value.sort_by.return_value = ["mock_pr"]
    mock_web_client.return_value = NonCallableMock()
    mock_pr_message_builder.return_value = NonCallableMock()
    return PostToDMs()


@patch("features.post_to_dms.PostToDMs._format_prs")
def test_run_no_users(mock_format_prs, instance):
    """Test the run method with no users"""
    mock_users = []
    with pytest.raises(NoUsersGiven) as exc:
        instance.run(mock_users, NonCallableMock())
        mock_format_prs.assert_called_once_with(instance.prs)
        assert (
            str(exc.value)
            == "No users were parsed to the function. Please specify users to message."
        )


@patch("features.post_to_dms.PostToDMs._post_thread_messages")
@patch("features.post_to_dms.PostToDMs._post_reminder_message")
@patch("features.post_to_dms.PostToDMs.validate_user")
@patch("features.post_to_dms.PostToDMs._format_prs")
def test_run_with_users(
    mock_format_prs,
    mock_validate_user,
    mock_post_reminder_message,
    mock_post_thread_messages,
    instance,
):
    """Test the run method with users"""
    mock_users = ["mock_user_1", "mock_user_2"]
    instance.run(mock_users, False)
    mock_format_prs.assert_called_once_with(["mock_pr"])
    for user in mock_users:
        mock_validate_user.assert_any_call(user)

        mock_reminder_thread_ts = mock_post_reminder_message.return_value
        mock_post_reminder_message.assert_called()
        mock_post_thread_messages.assert_any_call(
            instance.prs, mock_reminder_thread_ts, False
        )
    assert instance.channel == "mock_user_2"
    assert instance.user == "mock_user_2"


@patch("features.post_to_dms.PostToDMs._send_no_prs_found")
@patch("features.post_to_dms.PostToDMs._filter_thread_message")
def test_post_thread_messages(
    mock_filter_thread_message, mock_send_no_prs_found, instance
):
    """Test post thread messages"""
    mock_prs = ["pr1"]
    mock_filter_thread_message.return_value = False
    instance._post_thread_messages(mock_prs, "123", True)
    for pr in mock_prs:
        mock_filter_thread_message.assert_any_call(pr, "123", True)
    mock_send_no_prs_found.assert_called_once_with("123")


@patch("features.post_to_dms.PostToDMs._send_thread_react")
@patch("features.post_to_dms.PostToDMs._send_thread")
def test_filter_thread_message(mock_send_thread, mock_send_react, instance):
    """Test filter thread message"""
    mock_pr = NonCallableMock()
    res = instance._filter_thread_message(mock_pr, "123", True)
    mock_response = mock_send_thread.return_value
    mock_send_thread.assert_called_once_with(mock_pr, "123")
    mock_send_react.assert_called_once_with(
        mock_pr, mock_response.data["channel"], mock_response.data["ts"]
    )
    assert res == PRsFoundState.PRS_FOUND


def test_filter_thread_message_not_sent(instance):
    """Test filter thread message"""
    mock_pr = NonCallableMock()
    res = instance._filter_thread_message(mock_pr, "123", False)
    assert not res
