"""Tests for features.base_feature.PRMessageBuilder"""

# pylint: disable=W0212
# Disabling this as we need to access protected methods to test them
from unittest.mock import NonCallableMock, patch
import pytest
from features.base_feature import PRMessageBuilder
from pr_dataclass import PrData


@pytest.fixture(name="instance", scope="function")
@patch("features.base_feature.WebClient")
@patch("features.base_feature.GetGitHubPRs")
@patch("features.base_feature.get_token")
@patch("features.base_feature.get_repos")
@patch("features.base_feature.get_user_map")
def instance_fixture(_, _2, _3, _4, _5):
    """Provides a class instance for the tests"""
    return PRMessageBuilder()


@patch("features.base_feature.PRMessageBuilder.check_pr")
@patch("features.base_feature.PRMessageBuilder._construct_string")
def test_make_message(mock_construct_string, mock_check_pr, instance):
    """Test a message make call is made and string returned"""
    mock_pr_data = NonCallableMock()
    res = instance.make_message(mock_pr_data)
    mock_check_pr.assert_called_once_with(mock_pr_data)
    assert res == mock_construct_string.return_value


@patch("features.base_feature._slack_to_human_username")
@patch("features.base_feature.get_token")
@patch("features.base_feature.WebClient")
def test_construct_string_not_old(
    mock_web_client, mock_get_token, mock_name_translate, instance
):
    """Test a string is made correctly when the PR is old"""
    mock_data = NonCallableMock()
    mock_data.old = False
    mock_data.url = "mock_url"
    mock_data.pr_title = "mock_title"
    mock_data.user = "mock_user"
    res = instance._construct_string(mock_data)
    mock_web_client.assert_called_once_with(token=mock_get_token.return_value)
    mock_name_translate.assert_called_once_with(
        mock_web_client.return_value, "mock_user"
    )
    expected = f"Pull Request: <mock_url|mock_title>\nAuthor: {mock_name_translate.return_value}"
    assert res == expected


@patch("features.base_feature._slack_to_human_username")
@patch("features.base_feature.get_token")
@patch("features.base_feature.WebClient")
def test_construct_string_old(
    mock_web_client, mock_get_token, mock_name_translate, instance
):
    """Test a string is made correctly when the PR is old"""
    mock_data = NonCallableMock()
    mock_data.old = True
    mock_data.url = "mock_url"
    mock_data.pr_title = "mock_title"
    mock_data.user = "mock_user"
    res = instance._construct_string(mock_data)
    mock_web_client.assert_called_once_with(token=mock_get_token.return_value)
    mock_name_translate.assert_called_once_with(
        mock_web_client.return_value, "mock_user"
    )
    expected = (
        f"*This PR is older than 6 months. Consider closing it:*\n"
        f"Pull Request: <mock_url|mock_title>\nAuthor: {mock_name_translate.return_value}"
    )
    assert res == expected


@patch("features.base_feature.replace")
@patch("features.base_feature.timedelta")
@patch("features.base_feature.datetime")
@patch("features.base_feature.datetime_parser")
def test_check_pr_age_not_old(
    mock_datetime_parser, mock_datetime, mock_timedelta, _, instance
):
    """Test returns false since PR is not old"""
    mock_datetime_parser.parse.return_value.replace.return_value = 100
    mock_datetime.now.return_value.replace.return_value = 200
    mock_timedelta.return_value = 30 * 6
    res = instance._check_pr_age(100)
    mock_datetime_parser.parse.assert_called_once_with(100)
    mock_datetime_parser.parse.return_value.replace.assert_called_once_with(tzinfo=None)
    mock_datetime.now.assert_called_once_with()
    mock_datetime.now.return_value.replace.assert_called_once_with(tzinfo=None)
    mock_timedelta.assert_called_once_with(days=30 * 6)
    assert not res


@patch("features.base_feature.replace")
@patch("features.base_feature.timedelta")
@patch("features.base_feature.datetime")
@patch("features.base_feature.datetime_parser")
def test_check_pr_age_old(
    mock_datetime_parser, mock_datetime, mock_timedelta, _, instance
):
    """Test returns false since PR is  old"""
    mock_datetime_parser.parse.return_value.replace.return_value = 100
    mock_datetime.now.return_value.replace.return_value = 300
    mock_timedelta.return_value = 30 * 6
    res = instance._check_pr_age(100)
    mock_datetime_parser.parse.assert_called_once_with(100)
    mock_datetime_parser.parse.return_value.replace.assert_called_once_with(tzinfo=None)
    mock_datetime.now.assert_called_once_with()
    mock_datetime.now.return_value.replace.assert_called_once_with(tzinfo=None)
    mock_timedelta.assert_called_once_with(days=30 * 6)
    assert res


@patch("features.base_feature.PRMessageBuilder._check_pr_age")
@patch("features.base_feature.get_user_map")
def test_check_pr_info_found_name(mock_user_map, mock_check_pr_age, instance):
    """Test the dataclass is updated and name is found"""
    mock_data = PrData(
        pr_title="mock_title",
        user="mock_github",
        url="mock_url",
        created_at="mock_creation_date",
        draft=False,
        old=False,
    )
    mock_user_map.return_value = {"mock_github": "mock_slack"}
    mock_check_pr_age.return_value = True
    res = instance.check_pr(mock_data)
    assert res.user == "mock_slack"
    assert res.old


@patch("features.base_feature.PRMessageBuilder._check_pr_age")
@patch("features.base_feature.get_user_map")
def test_check_pr_info_unfound_name(mock_user_map, _, instance):
    """Test the dataclass is updated and name is not found"""
    mock_data = PrData(
        pr_title="mock_title",
        user="mock_user",
        url="mock_url",
        created_at="mock_creation_date",
        draft=False,
        old=False,
    )
    mock_user_map.return_value = {"mock_github": "mock_slack"}
    res = instance.check_pr(mock_data)
    assert res.user == "mock_user"
