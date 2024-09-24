"""
This module handles the HTTP requests and formatting to the GitHub REST Api.
It will get all open pull requests in provided repositories.
"""

from typing import List, Dict
import requests
from read_data import get_token
from pr_dataclass import PrData
from custom_exceptions import (
    RepoNotFound,
    UnknownHTTPError,
    BadGitHubToken,
)


class GetGitHubPRs:
    # pylint: disable=R0903
    # Disabling this as in the future there is likely to be more public functions.
    """
    This class handles getting the open PRs from the GitHub Rest API.
    """

    def __init__(self, repos: List[str], owner: str):
        """
        This method initialises the class with the following attributes.
        :param repos: A list of repositories to get pull requests for.
        :param repos: The owner of the above repositories.
        """
        self.repos = repos
        self.owner = owner
        self._http_handler = HTTPHandler()

    def run(self) -> List[PrData]:
        """
        This method is the entry point to the class.
        It runs the HTTP request methods and returns the responses.
        :return: The responses from the HTTP requests.
        """
        responses = self._request_all_repos_http()
        return self._parse_pr_to_dataclass(responses)

    def _request_all_repos_http(self) -> List[Dict]:
        """
        This method starts a request for each repository and returns a list of those PRs.
        :return: A dictionary of repos and their PRs.
        """
        responses = []
        for repo in self.repos:
            url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls"
            responses += self._http_handler.make_request(url)
        return responses

    @staticmethod
    def _parse_pr_to_dataclass(responses: List[Dict]) -> List[PrData]:
        """
        This module converts the responses from the HTTP request into Dataclasses to be more easily handled.
        :param responses: List of responses made from HTTP requests
        :return: Responses in dataclasses
        """
        responses_dataclasses = []
        for pr in responses:
            responses_dataclasses.append(
                PrData(
                    pr_title=f"{pr['title']} #{pr['number']}",
                    user=pr["user"]["login"],
                    url=pr["html_url"],
                    created_at=pr["created_at"],
                    draft=pr["draft"],
                )
            )
        return responses_dataclasses


class HTTPHandler:
    """
    This class makes the HTTP requests to the GitHub REST API.
    """

    def make_request(self, url: str) -> List[Dict]:
        """
        This method gets the HTTP response from the URL given and returns the response as a list.
        :param url: The URL to make the HTTP request to.
        :return: List of PRs.
        """
        response = self.get_http_response(url)
        return [response] if isinstance(response, dict) else response

    def get_http_response(self, url: str) -> List[Dict]:
        """
        This method sends a HTTP request to the GitHub Rest API endpoint and returns all open PRs from that repository.
        :param url: The URL to make the request to
        :return: The response in JSON form
        """
        headers = {"Authorization": "token " + get_token("GITHUB_TOKEN")}
        response = requests.get(url, headers=headers, timeout=60)
        self._validate_response(response)
        return response.json()

    @staticmethod
    def _validate_response(response: requests.get) -> None:
        """
        This method checks the status code of the HTTP response and handles exceptions accordingly.
        :param response: The response to check.
        """
        match response.status_code:
            case 200:
                pass
            case 401:
                raise BadGitHubToken(
                    "Your GitHub api token is invalid. Check that it hasn't expired."
                )
            case 404:
                raise RepoNotFound(
                    f'The repository at the url "{response.url}" could not be found.'
                )

            case _:
                raise UnknownHTTPError(
                    f"The HTTP response code is unknown and cannot be handled. Response: {response.status_code}"
                )
