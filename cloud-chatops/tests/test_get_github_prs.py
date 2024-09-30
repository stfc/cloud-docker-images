"""Tests for get_github_prs.GetGitHubPRs"""
# pylint: disable=W0212
# Disabling this as we need to access protected methods to test them
from unittest.mock import patch
import pytest
from get_github_prs import GetGitHubPRs
from pr_dataclass import PrData


@pytest.fixture(name="instance", scope="function")
def instance_fixture():
    """Creates a class fixture to use in the tests"""
    mock_repos = ["repo1", "repo2"]
    mock_owner = "mock_user"
    return GetGitHubPRs(mock_repos, mock_owner)


@patch("get_github_prs.GetGitHubPRs._request_all_repos_http")
@patch("get_github_prs.GetGitHubPRs._parse_pr_to_dataclass")
def test_run(
    mock_parse_pr_to_dataclass, mock_request_all_repos_http, instance
):
    """Tests the run method returns the correct object"""
    res = instance.run()
    mock_request_all_repos_http.assert_called_once_with()
    mock_parse_pr_to_dataclass.assert_called_once_with(
        mock_request_all_repos_http.return_value
    )
    assert res == mock_parse_pr_to_dataclass.return_value


@patch("get_github_prs.HTTPHandler.make_request")
def test_request_all_repos_http(mock_make_request, instance):
    """Test a request is made for each repo in the list"""
    mock_make_request.side_effect = [
        [f"https://api.github.com/repos/{instance.owner}/{repo}/pulls"]
        for repo in instance.repos
    ]
    res = instance._request_all_repos_http()
    for repo in instance.repos:
        mock_make_request.assert_any_call(
            f"https://api.github.com/repos/{instance.owner}/{repo}/pulls"
        )
    assert res == [
        f"https://api.github.com/repos/{instance.owner}/{repo}/pulls"
        for repo in instance.repos
    ]


def test_request_all_repos_http_none(instance):
    """Test that nothing is returned when no repos are given"""
    instance.repos = []
    res = instance._request_all_repos_http()
    assert res == []


def test_parse_pr_to_dataclass(instance):
    """Test that dataclasses are made correctly with the expected data"""
    mock_responses = [
        {
            "title": "mock_title1",
            "number": 1,
            "user": {"login": "mock_login1"},
            "html_url": "mock_html_url1",
            "created_at": "mock_created_at1",
            "draft": False,
        },
        {
            "title": "mock_title2",
            "number": 2,
            "user": {"login": "mock_login2"},
            "html_url": "mock_html_url2",
            "created_at": "mock_created_at2",
            "draft": False,
        },
    ]
    mock_dataclassses = [
        PrData(
            pr_title=f"{mock_responses[0]['title']} #{mock_responses[0]['number']}",
            user=mock_responses[0]["user"]["login"],
            url=mock_responses[0]["html_url"],
            created_at=mock_responses[0]["created_at"],
            draft=mock_responses[0]["draft"],
        ),
        PrData(
            pr_title=f"{mock_responses[1]['title']} #{mock_responses[1]['number']}",
            user=mock_responses[1]["user"]["login"],
            url=mock_responses[1]["html_url"],
            created_at=mock_responses[1]["created_at"],
            draft=mock_responses[1]["draft"],
        ),
    ]
    res = instance._parse_pr_to_dataclass(mock_responses)
    assert res == mock_dataclassses


def test_parse_pr_to_dataclass_none(instance):
    """Test nothing is returned when no dictionaries are given"""
    res = instance._parse_pr_to_dataclass([])
    assert res == []
