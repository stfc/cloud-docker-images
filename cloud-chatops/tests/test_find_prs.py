"""Tests for find_prs.py"""

from unittest.mock import patch, NonCallableMock
from datetime import datetime
import pytest
from requests.exceptions import HTTPError
from find_prs import FindPRs
from pr_dataclass import PR


# pylint: disable=R0801


@pytest.fixture(name="instance", scope="function")
def instance_fixture():
    """Creates a class fixture to use in the tests"""
    return FindPRs()


@patch("find_prs.PR")
@patch("find_prs.get_token")
@patch("find_prs.FindPRs.request_all_repos")
def test_run(mock_request_all_repos, mock_get_token, mock_pr_dataclass, instance):
    """Tests the run method returns the correct object"""
    mock_repo_1 = NonCallableMock()
    mock_repo_2 = NonCallableMock()
    mock_repo_1.created_at = 1
    mock_repo_2.created_at = 2
    mock_repos = {"owner1": [mock_repo_2, mock_repo_1]}
    res = instance.run(mock_repos)
    res = instance.sort_by(res, "created_at", True)
    assert instance.github_token == mock_get_token.return_value
    mock_get_token.assert_called_once_with("GITHUB_TOKEN")

    for owner in mock_repos:
        mock_request_all_repos.assert_any_call(owner, mock_repos.get(owner))

    mock_res = list(
        reversed([call.return_value for call in mock_pr_dataclass.call_arg_list])
    )
    assert res == mock_res


@patch("find_prs.FindPRs.make_request")
def test_request_all_repos(mock_make_request, instance):
    """Test a request is made for each repo in the list"""
    mock_make_request.side_effect = [["mock_response_1"], ["mock_response_2"]]
    res = instance.request_all_repos("mock_owner", ["mock_repo_1", "mock_repo_2"])
    mock_make_request.assert_any_call(
        "https://api.github.com/repos/mock_owner/mock_repo_1/pulls"
    )
    mock_make_request.assert_any_call(
        "https://api.github.com/repos/mock_owner/mock_repo_2/pulls"
    )
    assert res == ["mock_response_1", "mock_response_2"]


@patch("find_prs.requests")
def test_make_request(mock_requests, instance):
    """Test that requests are made and errors are raised."""
    mock_ok_request = NonCallableMock()
    mock_error_request = NonCallableMock()
    mock_error_request.raise_for_status.side_effect = HTTPError
    mock_requests.get.side_effect = [mock_ok_request, mock_error_request]
    res = instance.make_request(
        "https://api.github.com/repos/mock_owner/mock_repo/pulls"
    )
    assert res == mock_ok_request.json.return_value
    with pytest.raises(HTTPError):
        instance.make_request(
            "https://api.github_wrong.com/repos/mock_owner/mock_repo/pulls"
        )


MOCK_PR_1 = PR(
    title="mock_title #1",
    author="mock_author",
    url="https://api.github.com/repos/mock_owner/mock_repo/pulls",
    stale=False,
    draft=False,
    labels=["mock_label"],
    repository="mock_repo",
    created_at=datetime.strptime("2024-11-15T07:33:56Z", "%Y-%m-%dT%H:%M:%SZ"),
)
MOCK_PR_2 = PR(
    title="mock_title #2",
    author="mock_author_2",
    url="https://api.github.com/repos/mock_owner/mock_repo/pulls",
    stale=True,
    draft=True,
    labels=["mock_label"],
    repository="mock_repo_2",
    created_at=datetime.strptime("2024-10-15T07:33:56Z", "%Y-%m-%dT%H:%M:%SZ"),
)


def test_sort_by(instance):
    """Test the list is sorted correctly."""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    res = instance.sort_by(mock_pr_list, "created_at")
    assert res == list(reversed(mock_pr_list))

    res_reversed = instance.sort_by(mock_pr_list, "created_at", True)
    assert res_reversed == mock_pr_list


def test_sort_by_fails(instance):
    """Test sort raises an error when sorting by unknown attribute"""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    with pytest.raises(ValueError) as exc:
        instance.sort_by(mock_pr_list, "unknown")
        assert str(exc.value) == "Unable to sort list by unknown"


def test_filter_by(instance):
    """Test the list is filtered correctly."""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    res = instance.filter_by(mock_pr_list, "repository", "mock_repo")
    assert res == [MOCK_PR_1]


def test_filter_by_fails(instance):
    """Test filter raises an error when filtering by unknown attribute"""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    with pytest.raises(ValueError) as exc:
        instance.filter_by(mock_pr_list, "unknown", "some_value")
        assert str(exc.value) == "Unable to filter list by unknown"
