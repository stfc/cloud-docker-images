import pytest
from unittest.mock import NonCallableMock, patch, MagicMock
from slack_sdk.errors import SlackApiError
from features.base_feature import BaseFeature


@pytest.fixture(name="instance", scope="function")
@patch("features.base_feature.WebClient")
@patch("features.base_feature.GetGitHubPRs")
@patch("features.base_feature.get_token")
@patch("features.base_feature.get_repos")
@patch("features.base_feature.get_user_map")
def instance(
    mock_get_user_map,
    mock_get_repos,
    mock_get_token,
    mock_get_github_prs,
    mock_web_client,
):
    """This fixture provides a class instance for the tests"""
    mock_get_user_map.return_value = {"mock_github": "mock_slack"}
    mock_get_repos.return_value = ["mock_repo1", "mock_repo2"]
    mock_get_token.return_value = "mock_slack_token"
    mock_get_github_prs.run.return_value = []
    mock_web_client.return_value = NonCallableMock()
    return BaseFeature()


def test_github_to_slack_username_valid(instance):
    """Test the github to slack name translation works"""
    res = instance._github_to_slack_username("mock_github")
    assert res == "mock_slack"


def test_github_to_slack_username_invalid(instance):
    """Test the github to slack name translation works"""
    res = instance._github_to_slack_username("mock_github_not_found")
    assert res == "mock_github_not_found"


def test_slack_to_human_username_valid(instance):
    """Test the slack member id to real name works"""
    instance.client.users_profile_get.return_value = {
        "profile": {"real_name": "mock_name"}
    }
    res = instance._slack_to_human_username("mock_member_id")
    instance.client.users_profile_get.assert_called_once_with(user="mock_member_id")
    assert res == "mock_name"


def test_slack_to_human_username_invalid(instance):
    """Test the slack member id to real name works"""
    instance.client.users_profile_get.side_effect = SlackApiError("", "")
    res = instance._slack_to_human_username("mock_member_id")
    assert res == "mock_member_id"


def test_post_reminder_message(instance):
    """Test a message is posted"""
    return_obj = MagicMock()
    return_obj.data = {"ts": 100}
    return_obj.__getitem__.side_effect = [True]
    instance.client.chat_postMessage.return_value = return_obj
    res = instance._post_reminder_message()
    instance.client.chat_postMessage.assert_called_once_with(
        channel=instance.channel,
        text="Here are the outstanding PRs as of today:",
    )
    assert res == 100


def test_post_reminder_message_fails(instance):
    """Test a message is not posted"""
    instance.client.chat_postMessage.return_value = {"ok": False}
    with pytest.raises(AssertionError):
        instance._post_reminder_message()


def test_send_no_prs_found(instance):
    """Test a message is posted"""
    instance.client.chat_postMessage.return_value = {"ok": True}
    instance._send_no_prs_found(100)
    instance.client.chat_postMessage.assert_called_once_with(
        channel=instance.channel,
        thread_ts=100,
        text="There are no outstanding pull requests open.",
        unfurl_links=False,
    )


def test_send_no_prs_found_fails(instance):
    """Test a message is not posted"""
    instance.client.chat_postMessage.return_value = {"ok": False}
    with pytest.raises(AssertionError):
        instance._send_no_prs_found(100)


@patch("features.base_feature.PRMessageBuilder")
def test_send_thread(mock_pr_message_builder, instance):
    """Test a message is sent"""
    mock_pr_data = NonCallableMock()
    mock_pr_message_builder.return_value.make_message.return_value = "mock_message"
    instance.client.chat_postMessage.return_value = {"ok": True}
    res = instance._send_thread(mock_pr_data, "100")
    mock_pr_message_builder.return_value.make_message.assert_called_once_with(
        mock_pr_data
    )
    instance.client.chat_postMessage.assert_called_once_with(
        channel=instance.channel,
        thread_ts="100",
        text="mock_message",
        unfurl_links=False,
    )
    assert res == instance.client.chat_postMessage.return_value


@patch("features.base_feature.PRMessageBuilder")
def test_send_thread_fails(_, instance):
    """Test a message is not sent"""
    instance.client.chat_postMessage.return_value = {"ok": False}
    with pytest.raises(AssertionError):
        res = instance._send_thread(NonCallableMock(), "100")


def test_send_thread_react_no_reactions(instance):
    """Test no reactions are added"""
    mock_pr_data = NonCallableMock()
    mock_pr_data.old = False
    mock_pr_data.draft = False
    instance._send_thread_react(mock_pr_data, "mock_channel", "100")
    instance.client.reactions_add.assert_not_called()


def test_send_thread_react_fails_to_add(instance):
    """Test reaction fails"""
    mock_pr_data = NonCallableMock()
    mock_pr_data.old = True
    mock_pr_data.draft = True
    instance.client.reactions_add.side_effect = [{"ok": True}, {"ok": False}]
    with pytest.raises(AssertionError):
        instance._send_thread_react(mock_pr_data, "mock_channel", "100")


def test_send_thread_react_with_reactions(instance):
    """Test all reactions are added"""
    mock_pr_data = NonCallableMock()
    mock_pr_data.old = True
    mock_pr_data.draft = True
    instance.client.reactions_add.return_value = {"ok": True}
    instance._send_thread_react(mock_pr_data, "mock_channel", "100")
    instance.client.reactions_add.assert_any_call(
        channel="mock_channel", name="alarm_clock", timestamp="100"
    )
    instance.client.reactions_add.assert_any_call(
        channel="mock_channel", name="scroll", timestamp="100"
    )
