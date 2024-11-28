"""Tests for features.base_feature.PRMessageBuilder"""

# pylint: disable=W0212
# Disabling this as we need to access protected methods to test them
from unittest.mock import NonCallableMock, patch
from datetime import datetime
import pytest
from slack_sdk.errors import SlackApiError
from features.base_feature import PRMessageBuilder
from pr_dataclass import PR


@pytest.fixture(name="instance", scope="function")
@patch("features.base_feature.WebClient")
@patch("features.base_feature.FindPRs")
@patch("features.base_feature.get_token")
@patch("features.base_feature.get_config")
def instance_fixture(_, _2, _3, _4):
    """Provides a class instance for the tests"""
    return PRMessageBuilder()


@patch("features.base_feature.PRMessageBuilder.add_user_info_and_age")
@patch("features.base_feature.PRMessageBuilder._construct_string")
def test_make_message(mock_construct_string, mock_add_user_info_and_age, instance):
    """Test a message make call is made and string returned"""
    mock_pr_data = NonCallableMock()
    res = instance.make_message(mock_pr_data)
    mock_add_user_info_and_age.assert_called_once_with(mock_pr_data)
    assert res == mock_construct_string.return_value


@patch("features.base_feature.get_token")
@patch("features.base_feature.WebClient")
def test_construct_string_not_old(mock_web_client, mock_get_token, instance):
    """Test a string is made correctly when the PR is old"""
    mock_web_client.return_value.users_profile_get.return_value = {
        "profile": {"real_name": "mock_real_name"}
    }
    mock_data = NonCallableMock()
    mock_data.stale = False
    mock_data.url = "mock_url"
    mock_data.title = "mock_title"
    mock_data.author = "mock_user"
    res = instance._construct_string(mock_data)
    mock_web_client.assert_called_once_with(token=mock_get_token.return_value)
    expected = "Pull Request: <mock_url|mock_title>\nAuthor: mock_real_name"
    assert res == expected


@patch("features.base_feature.get_token")
@patch("features.base_feature.WebClient")
def test_construct_string_old(mock_web_client, mock_get_token, instance):
    """Test a string is made correctly when the PR is old"""
    mock_web_client.return_value.users_profile_get.return_value = {
        "profile": {"real_name": "mock_real_name"}
    }
    mock_data = NonCallableMock()
    mock_data.old = True
    mock_data.url = "mock_url"
    mock_data.title = "mock_title"
    mock_data.user = "mock_user"
    res = instance._construct_string(mock_data)
    mock_web_client.assert_called_once_with(token=mock_get_token.return_value)
    expected = (
        "*This PR is older than 30 days. Consider closing it:*\n"
        "Pull Request: <mock_url|mock_title>\nAuthor: mock_real_name"
    )
    assert res == expected


@patch("features.base_feature.get_token")
@patch("features.base_feature.WebClient")
def test_construct_string_fails_lookup(mock_web_client, _2, instance):
    """Test if the name lookup fails the given user is printed."""
    mock_web_client.return_value.users_profile_get.side_effect = SlackApiError("", "")
    mock_data = NonCallableMock()
    mock_data.stale = True
    mock_data.url = "mock_url"
    mock_data.title = "mock_title"
    mock_data.author = "mock_user"
    res = instance._construct_string(mock_data)
    expected = (
        "*This PR is older than 30 days. Consider closing it:*\n"
        "Pull Request: <mock_url|mock_title>\nAuthor: mock_user"
    )
    assert res == expected


@patch("features.base_feature.get_config")
def test_check_pr_info_found_name_and_is_new(mock_get_config, instance):
    """Test the dataclass is updated and name is found"""
    mock_data = PR(
        title="mock_title",
        author="mock_github",
        url="mock_url",
        stale=False,
        draft=False,
        labels=[],
        repository="mock_repo",
        created_at=datetime.now(),
    )
    mock_get_config.return_value = {"mock_github": "mock_slack"}
    res = instance.add_user_info_and_age(mock_data)
    mock_get_config.assert_called_once_with("user-map")
    assert res.author == "mock_slack"
    assert not res.stale


@patch("features.base_feature.get_config")
def test_check_pr_info_found_name_and_is_old(mock_get_config, instance):
    """Test the dataclass is updated and name is found"""
    mock_data = PR(
        title="mock_title",
        author="mock_github",
        url="mock_url",
        stale=True,
        draft=False,
        labels=[],
        repository="mock_repo",
        created_at=datetime.now(),
    )
    mock_get_config.return_value = {"mock_github": "mock_slack"}
    res = instance.add_user_info_and_age(mock_data)
    mock_get_config.assert_called_once_with("user-map")
    assert res.author == "mock_slack"
    assert res.stale


@patch("features.base_feature.get_config")
def test_check_pr_info_not_found_name(mock_get_config, instance):
    """Test the dataclass is updated and name is not found"""
    mock_data = PR(
        title="mock_title",
        author="mock_user",
        url="mock_url",
        stale=False,
        draft=False,
        labels=[],
        repository="mock_repo",
        created_at=datetime.now(),
    )
    mock_get_config.return_value = {"mock_github": "mock_slack"}
    res = instance.add_user_info_and_age(mock_data)
    mock_get_config.assert_called_once_with("user-map")
    assert res.author == "mock_user"
