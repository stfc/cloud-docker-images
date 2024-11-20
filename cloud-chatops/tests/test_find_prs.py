"""Tests for find_prs.py"""

from unittest.mock import patch, NonCallableMock
import pytest
from requests.exceptions import HTTPError
from find_prs import FindPRs
from pr_dataclass import PRProps


@pytest.fixture(name="instance", scope="function")
def instance_fixture():
    """Creates a class fixture to use in the tests"""
    return FindPRs()


@patch("find_prs.PR")
@patch("find_prs.get_token")
@patch("find_prs.FindPRs.request_all_repos")
def test_run_with_sort(
    mock_request_all_repos, mock_get_token, mock_pr_dataclass, instance
):
    """Tests the run method returns the correct object"""
    mock_repo_1 = NonCallableMock()
    mock_repo_2 = NonCallableMock()
    mock_repo_1.created_at = 1
    mock_repo_2.created_at = 2
    mock_repos = {"owner1": [mock_repo_2, mock_repo_1]}
    res = instance.run(mock_repos, (PRProps.CREATED_AT, True))
    assert instance.github_token == mock_get_token.return_value
    mock_get_token.assert_called_once_with("GITHUB_TOKEN")

    for owner in mock_repos:
        mock_request_all_repos.assert_any_call(owner, mock_repos.get(owner))
    for call in mock_request_all_repos.calls():
        mock_pr_dataclass.assert_any_call(call.return_value)

    mock_res = list(reversed([call.return_value for call in mock_pr_dataclass.calls()]))
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
