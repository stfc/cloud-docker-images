from unittest.mock import patch, NonCallableMock
import pytest
from get_github_prs import GetGitHubPRs, HTTPHandler
from pr_dataclass import PrData
from errors import BadGitHubToken, RepoNotFound, UnknownHTTPError


@pytest.fixture(name="instance_GetGitHubPRs", scope="function")
def instance_GetGitHubPRs():
    """Creates a class pytest.fixture to use in the tests"""
    mock_repos = ["repo1", "repo2"]
    mock_owner = "mock_user"
    return GetGitHubPRs(mock_repos, mock_owner)


@pytest.fixture(name="instance_HTTPHandler", scope="function")
def instance_HTTPHandler():
    """Creates a class pytest.fixture to use in the tests"""
    return HTTPHandler()


@patch("get_github_prs.GetGitHubPRs._request_all_repos_http")
@patch("get_github_prs.GetGitHubPRs._parse_pr_to_dataclass")
def test_run(
    mock_parse_pr_to_dataclass, mock_request_all_repos_http, instance_GetGitHubPRs
):
    """Tests the run method returns the correct object"""
    res = instance_GetGitHubPRs.run()
    mock_request_all_repos_http.assert_called_once_with()
    mock_parse_pr_to_dataclass.assert_called_once_with(
        mock_request_all_repos_http.return_value
    )
    assert res == mock_parse_pr_to_dataclass.return_value


@patch("get_github_prs.HTTPHandler.make_request")
def test_request_all_repos_http(mock_make_request, instance_GetGitHubPRs):
    """Test a request is made for each repo in the list"""
    mock_make_request.side_effect = [
        [f"https://api.github.com/repos/{instance_GetGitHubPRs.owner}/{repo}/pulls"]
        for repo in instance_GetGitHubPRs.repos
    ]
    res = instance_GetGitHubPRs._request_all_repos_http()
    for repo in instance_GetGitHubPRs.repos:
        mock_make_request.assert_any_call(
            f"https://api.github.com/repos/{instance_GetGitHubPRs.owner}/{repo}/pulls"
        )
    assert res == [
        f"https://api.github.com/repos/{instance_GetGitHubPRs.owner}/{repo}/pulls"
        for repo in instance_GetGitHubPRs.repos
    ]


def test_request_all_repos_http_none(instance_GetGitHubPRs):
    """Test that nothing is returned when no repos are given"""
    instance_GetGitHubPRs.repos = []
    res = instance_GetGitHubPRs._request_all_repos_http()
    assert res == []


def test_parse_pr_to_dataclass(instance_GetGitHubPRs):
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
    res = instance_GetGitHubPRs._parse_pr_to_dataclass(mock_responses)
    assert res == mock_dataclassses


def test_parse_pr_to_dataclass_none(instance_GetGitHubPRs):
    """Test nothing is returned when no dictionaries are given"""
    res = instance_GetGitHubPRs._parse_pr_to_dataclass([])
    assert res == []


@patch("get_github_prs.HTTPHandler._validate_response")
@patch("get_github_prs.requests")
@patch("get_github_prs.get_token")
def test_make_request_calls(
    mock_get_token, mock_requests, mock_validate_response, instance_HTTPHandler
):
    """Test the get and validate methods are called for a request"""
    mock_url = "https://mymock.mock"
    mock_headers = {"Authorization": "token " + "mock_token"}
    mock_get_token.return_value = "mock_token"
    instance_HTTPHandler.make_request(mock_url)
    mock_requests.get.assert_called_once_with(
        mock_url, headers=mock_headers, timeout=60
    )
    mock_validate_response.assert_called_once_with(mock_requests.get.return_value)


@patch("get_github_prs.HTTPHandler._validate_response")
@patch("get_github_prs.requests")
@patch("get_github_prs.get_token")
def test_make_request_return_single(_, mock_requests, _2, instance_HTTPHandler):
    """
    Test the return type when a dictionarie is returned.
    This simulates one/none pr is being returned.
    """
    mock_requests.get.return_value = NonCallableMock()
    mock_requests.get.return_value.json.return_value = {}
    res = instance_HTTPHandler.make_request("mock_url")
    mock_requests.get.return_value.json.assert_called_once()
    assert res == [{}]


@patch("get_github_prs.HTTPHandler._validate_response")
@patch("get_github_prs.requests")
@patch("get_github_prs.get_token")
def test_make_request_return_multiple(_, mock_requests, _2, instance_HTTPHandler):
    """
    Test the return type when lists are returned.
    This simulates multiple prs being returned.
    """
    mock_requests.get.return_value = NonCallableMock()
    mock_requests.get.return_value.json.return_value = [{}, {}]
    res = instance_HTTPHandler.make_request("mock_url")
    mock_requests.get.return_value.json.assert_called_once()
    assert res == [{}, {}]


@pytest.mark.parametrize(
    "status_code,error",
    [
        (401, BadGitHubToken),
        (404, RepoNotFound),
        (None, UnknownHTTPError),
        ("200", UnknownHTTPError),
        (999, UnknownHTTPError),
    ],
)
def test_validate_response_failed(status_code, error, instance_HTTPHandler):
    """Test the validate method raises errors for cases."""
    mock_response = NonCallableMock()
    mock_response.status_code = status_code
    with pytest.raises(error):
        instance_HTTPHandler._validate_response(mock_response)


def test_validate_response_passed(instance_HTTPHandler):
    """Test the validate method raises errors for case status 200."""
    mock_response = NonCallableMock()
    mock_response.status_code = 200
    instance_HTTPHandler._validate_response(mock_response)
