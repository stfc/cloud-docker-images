"""Tests for gitlab.py"""

from unittest.mock import patch, NonCallableMock
from datetime import datetime
import pytest
from requests.exceptions import HTTPError
from helper.data import PR, sort_by, filter_by
from find_pr_api.gitlab import FindPRs


# pylint: disable=R0801
@pytest.fixture(name="instance", scope="function")
def instance_fixture():
    """Creates a class fixture to use in the tests"""
    return FindPRs()


@patch("find_pr_api.gitlab.PR")
@patch("find_pr_api.gitlab.FindPRs.make_request")
def test_run(mock_make_request, mock_data, instance):
    """Tests the run method returns the correct object"""
    mock_project_1 = NonCallableMock()
    mock_project_2 = NonCallableMock()
    mock_project_1.created_at = 1
    mock_project_2.created_at = 2
    mock_projects = [mock_project_2, mock_project_1]
    res = instance.run(mock_projects, "mock_token")
    res = sort_by(res, "created_at", True)

    for project in mock_projects:
        mock_make_request.assert_any_call(project, "mock_token")

    mock_res = list(reversed([call.return_value for call in mock_data.call_arg_list]))
    assert res == mock_res


@patch("find_pr_api.gitlab.requests")
def test_make_request_ok(mock_requests, instance):
    """Test that a request is made."""
    mock_ok_request = NonCallableMock()
    mock_requests.get.side_effect = [mock_ok_request]
    res = instance.make_request(
        "https://gitlab.stfc.ac.uk/api/v4/projects/mock-group%2Fmock_project/"
        "merge_requests?state=opened&scope=all",
        "mock_token"
    )
    assert res == mock_ok_request.json.return_value


@patch("find_pr_api.gitlab.requests")
def test_make_request_fail(mock_requests, instance):
    """Test that a request is made and an error is raised simulating a failed request."""
    mock_error_request = NonCallableMock()
    mock_error_request.raise_for_status.side_effect = HTTPError
    mock_requests.get.side_effect = [mock_error_request]
    with pytest.raises(HTTPError):
        instance.make_request(
            "https://gitlab.stfc.ac.uk/api/v4/projects/mock-group%2Fmock-project/"
            "merge_requests?state=opened&scope=all",
            "mock_token",
        )


MOCK_PR_1 = PR(
    title="mock_title #1",
    author="mock-user",
    url="https://gitlab.stfc.ac.uk/mock-group/mock-project/-/merge_requests/205",
    stale=False,
    draft=False,
    labels=["mock_label"],
    repository="mock-project",
    created_at=datetime.fromisoformat("2025-01-21T08:45:21.201+00:00"),
)
MOCK_PR_2 = PR(
    title="mock_title #2",
    author="mock_author_2",
    url="https://gitlab.stfc.ac.uk/mock-group/mock-project/-/merge_requests/204",
    stale=True,
    draft=True,
    labels=["mock_label"],
    repository="mock-project-2",
    created_at=datetime.fromisoformat("2024-12-15T07:33:56.000+00:00"),
)


def test_sort_by():
    """Test the list is sorted correctly."""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    res = sort_by(mock_pr_list, "created_at")
    assert res == list(reversed(mock_pr_list))

    res_reversed = sort_by(mock_pr_list, "created_at", True)
    assert res_reversed == mock_pr_list


def test_sort_by_fails():
    """Test sort raises an error when sorting by unknown attribute"""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    with pytest.raises(ValueError):
        sort_by(mock_pr_list, "unknown")


def test_filter_by():
    """Test the list is filtered correctly."""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    res = filter_by(mock_pr_list, "repository", "mock-project")
    assert res == [MOCK_PR_1]


def test_filter_by_fails():
    """Test filter raises an error when filtering by unknown attribute"""
    mock_pr_list = [MOCK_PR_1, MOCK_PR_2]
    with pytest.raises(ValueError):
        filter_by(mock_pr_list, "unknown", "some_value")
