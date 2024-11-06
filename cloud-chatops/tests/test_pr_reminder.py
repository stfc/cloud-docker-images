"""Tests for features.pr_reminder"""

# pylint: disable=W0212
# Disabling this as we need to access protected methods to test them
from unittest.mock import NonCallableMock, patch
import pytest
from features.pr_reminder import PostPRsToSlack
from features.base_feature import DEFAULT_CHANNEL


@pytest.fixture(name="instance", scope="function")
@patch("features.base_feature.WebClient")
@patch("features.base_feature.GetGitHubPRs")
@patch("features.base_feature.get_token")
@patch("features.base_feature.get_config")
def instance_fixture(
    _,
    mock_get_token,
    mock_get_github_prs,
    mock_web_client,
):
    """This fixture provides a class instance for the tests"""
    mock_get_token.return_value = "mock_slack_token"
    mock_get_github_prs.return_value.run.return_value = []
    mock_web_client.return_value = NonCallableMock()
    return PostPRsToSlack()


@patch("features.pr_reminder.PostPRsToSlack._post_reminder_message")
@patch("features.pr_reminder.PostPRsToSlack._post_thread_messages")
def test_run_no_channel(mock_thread, mock_reminder, instance):
    """Test the feature calls the right methods and doesn't set the channel."""
    instance.run()
    mock_reminder.assert_called_once()
    mock_thread.assert_called_once_with(instance.prs, mock_reminder.return_value)
    assert instance.channel == DEFAULT_CHANNEL


@patch("features.pr_reminder.PostPRsToSlack._post_reminder_message")
@patch("features.pr_reminder.PostPRsToSlack._post_thread_messages")
def test_run_with_channel(mock_thread, mock_reminder, instance):
    """Test the feature calls the right methods and doesn't set the channel."""
    instance.run("mock_channel")
    mock_reminder.assert_called_once()
    mock_thread.assert_called_once_with(instance.prs, mock_reminder.return_value)
    assert instance.channel == "mock_channel"


@patch("features.pr_reminder.BaseFeature._send_thread_react")
@patch("features.pr_reminder.BaseFeature._send_no_prs_found")
def test_post_thread_messages_none_found(mock_no_prs_found, _, instance):
    """Test the no prs found message is sent"""
    instance._post_thread_messages([], "100")
    mock_no_prs_found.assert_called_once_with("100")


@patch("features.pr_reminder.BaseFeature._send_thread")
@patch("features.pr_reminder.BaseFeature._send_thread_react")
@patch("features.pr_reminder.BaseFeature._send_no_prs_found")
def test_post_thread_messages(_, mock_send_thread_react, mock_send_thread, instance):
    """Test the no prs found message is sent"""
    mock_response = NonCallableMock()
    mock_response.data = {
        "channel": "mock_channel",
        "ts": "100",
    }
    mock_send_thread.return_value = mock_response
    instance._post_thread_messages(["mock1", "mock2"], "100")
    mock_send_thread.assert_any_call("mock1", "100")
    mock_send_thread.assert_any_call("mock2", "100")
    mock_send_thread_react.assert_any_call("mock1", "mock_channel", "100")
    mock_send_thread_react.assert_any_call("mock2", "mock_channel", "100")
