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


@patch("features.base_feature.PRMessageBuilder._check_pr_info")
@patch("features.base_feature.PRMessageBuilder._construct_string")
def test_make_message(mock_construct_string, mock_check_pr_info, instance):
    """Test a message make call is made and string returned"""
    mock_pr_data = NonCallableMock()
    res = instance.make_message(mock_pr_data)
    mock_check_pr_info.assert_called_once_with(mock_pr_data)
    assert res == mock_construct_string.return_value


@patch("features.base_feature.PRMessageBuilder._slack_to_human_username")
def test_construct_string_not_old(mock_name_translate, instance):
    """Test a string is made correctly when the PR is not old"""
    mock_data = NonCallableMock()
    mock_data.old = False
    mock_data.url = "mock_url"
    mock_data.pr_title = "mock_title"
    mock_data.user = "mock_user"
    res = instance._construct_string(mock_data)
    mock_name_translate.assert_called_once_with("mock_user")
    assert (
        res
        == f"Pull Request: <mock_url|mock_title>\nAuthor: {mock_name_translate.return_value}"
    )


@patch("features.base_feature.PRMessageBuilder._slack_to_human_username")
def test_construct_string(mock_name_translate, instance):
    """Test a string is made correctly when the PR is old"""
    mock_data = NonCallableMock()
    mock_data.old = True
    mock_data.url = "mock_url"
    mock_data.pr_title = "mock_title"
    mock_data.user = "mock_user"
    res = instance._construct_string(mock_data)
    mock_name_translate.assert_called_once_with("mock_user")
    expected = (f"*This PR is older than 6 months. Consider closing it:*\n"
                f"Pull Request: <mock_url|mock_title>\nAuthor: {mock_name_translate.return_value}")
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
@patch("features.base_feature.BaseFeature._github_to_slack_username")
def test_check_pr_info(mock_translate_name, mock_check_pr_age, instance):
    """Test the dataclass is updated"""
    mock_data = PrData(
        pr_title="mock_title",
        user="mock_user",
        url="mock_user",
        created_at="mock_creation_date",
        draft=False,
        old=False,
    )
    mock_translate_name.return_value = "mock_changed_user"
    mock_check_pr_age.return_value = True
    res = instance._check_pr_info(mock_data)
    assert res.user == "mock_changed_user"
    assert res.old
