"""
This module handles the HTTP requests and formatting to the GitHub REST Api.
It will get all open pull requests in provided repositories.
"""

from typing import List, Dict
from datetime import datetime
import requests
from read_data import get_token
from pr_dataclass import PrData
from errors import (
    RepoNotFound,
    UnknownHTTPError,
    BadGitHubToken,
)


class GetGitHubPRs:
    # pylint: disable=R0903
    # Disabling this as we only need one public method
    """
    This class handles getting the open PRs from the GitHub Rest API.
    """

    def __init__(self, repos: Dict[str, List]):
        """
        This method initialises the class with the following attributes.
        :param repos: A list of repositories to get pull requests for.
        :param repos: The owner of the above repositories.
        """
        self.repos = repos
        self._http_handler = HTTPHandler()

    def run(self) -> List[PrData]:
        """
        This method is the entry point to the class.
        It runs the HTTP request methods and returns the responses.
        :return: The responses from the HTTP requests.
        """
        responses = []
        for owner in self.repos:
            responses += self._request_all_repos_http(owner, self.repos.get(owner))
        return self._parse_pr_to_dataclass(responses)

    def _request_all_repos_http(self, owner: str, repos: List[str]) -> List[Dict]:
        """
        This method starts a request for each repository and returns a list of those PRs.
        :param owner: The organisation for repos
        :param repos: List of repository names
        :return: A list of PRs stored as dictionaries
        """
        responses = []
        for repo in repos:
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
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
                    created_at=datetime.strptime(
                        pr["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    draft=pr["draft"],
                )
            )
        sorted_responses = sorted(responses_dataclasses, key=lambda x: x.created_at)
        return sorted_responses


class HTTPHandler:
    # pylint: disable=R0903
    # Disabling this as we only need one public method
    """
    This class makes the HTTP requests to the GitHub REST API.
    """

    def make_request(self, url: str) -> List[Dict]:
        """
        This method sends a HTTP request to the GitHub Rest API endpoint and returns all open PRs from that repository.
        :param url: The URL to make the request to
        :return: The response in JSON form
        """
        headers = {"Authorization": "token " + get_token("GITHUB_TOKEN")}
        response = requests.get(url, headers=headers, timeout=60)
        self._validate_response(response)
        json_response = response.json()
        return [json_response] if isinstance(json_response, dict) else json_response

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
