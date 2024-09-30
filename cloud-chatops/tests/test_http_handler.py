"""Tests for get_github_prs.HTTPHandler"""
from unittest.mock import patch, NonCallableMock
import pytest
from get_github_prs import HTTPHandler
from errors import BadGitHubToken, RepoNotFound, UnknownHTTPError


@pytest.fixture(name="instance", scope="function")
def instance_fixture():
    """Creates a class fixture to use in the tests"""
    return HTTPHandler()


@patch("get_github_prs.HTTPHandler._validate_response")
@patch("get_github_prs.requests")
@patch("get_github_prs.get_token")
def test_make_request_calls(
    mock_get_token, mock_requests, mock_validate_response, instance
):
    """Test the get and validate methods are called for a request"""
    mock_url = "https://mymock.mock"
    mock_headers = {"Authorization": "token " + "mock_token"}
    mock_get_token.return_value = "mock_token"
    instance.make_request(mock_url)
    mock_requests.get.assert_called_once_with(
        mock_url, headers=mock_headers, timeout=60
    )
    mock_validate_response.assert_called_once_with(mock_requests.get.return_value)


@patch("get_github_prs.HTTPHandler._validate_response")
@patch("get_github_prs.requests")
@patch("get_github_prs.get_token")
def test_make_request_return_single(_, mock_requests, _2, instance):
    """
    Test the return type when a dictionarie is returned.
    This simulates one/none pr is being returned.
    """
    mock_requests.get.return_value = NonCallableMock()
    mock_requests.get.return_value.json.return_value = {}
    res = instance.make_request("mock_url")
    mock_requests.get.return_value.json.assert_called_once()
    assert res == [{}]


@patch("get_github_prs.HTTPHandler._validate_response")
@patch("get_github_prs.requests")
@patch("get_github_prs.get_token")
def test_make_request_return_multiple(_, mock_requests, _2, instance):
    """
    Test the return type when lists are returned.
    This simulates multiple prs being returned.
    """
    mock_requests.get.return_value = NonCallableMock()
    mock_requests.get.return_value.json.return_value = [{}, {}]
    res = instance.make_request("mock_url")
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
def test_validate_response_failed(status_code, error, instance):
    """Test the validate method raises errors for cases."""
    mock_response = NonCallableMock()
    mock_response.status_code = status_code
    with pytest.raises(error):
        instance._validate_response(mock_response)


def test_validate_response_passed(instance):
    """Test the validate method raises errors for case status 200."""
    mock_response = NonCallableMock()
    mock_response.status_code = 200
    instance._validate_response(mock_response)