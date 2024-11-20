"""This module finds all open pull requests from given repositories."""

from typing import List, Dict, Union, Tuple
import requests
from read_data import get_token
from pr_dataclass import PR, PRProps


class FindPRs:
    """This class finds all open pull requests in the given repositories. It can also sort them chronologically."""

    def __init__(self, github_token=""):
        """
        Initialise the class with a GitHub token if not using run as entry point.
        :param github_token: GitHub REST API token.
        """
        self.github_token = github_token

    def run(
        self, repos: Dict[str, List], sort: Union[Tuple[PRProps, bool], None] = None
    ) -> List[PR]:
        """
        Finds all open pull requests and returns them as a list of dataclasses.
        :param repos: Dictionary of repository names and owners.
        :param sort: Sort the list by property in ascending or descending order.
        :return: List of PRs
        """
        if not self.github_token:
            self.github_token = get_token("GITHUB_TOKEN")

        raw_responses = []
        for organisation in repos:
            raw_responses += self.request_all_repos(
                organisation, repos.get(organisation)
            )

        dataclass_list = [PR.from_json(response) for response in raw_responses]

        if sort:
            dataclass_list = sorted(
                dataclass_list,
                key=lambda pr: getattr(pr, str(sort[0]).split(sep=".")[1].lower()),
                reverse=sort[1],
            )

        return dataclass_list

    def request_all_repos(
        self, organisation: str, repositories: List[str]
    ) -> List[Dict]:
        """
        Makes a request for each repository and returns a list of those PRs.
        :param organisation: The repository owner
        :param repositories: List of repository names
        :return: A list of PRs stored as dictionaries
        """
        responses = []
        for repo in repositories:
            url = f"https://api.github.com/repos/{organisation}/{repo}/pulls"
            responses += self.make_request(url)
        return responses

    def make_request(self, url: str) -> List[Dict]:
        """
        Send an HTTP request to the GitHub Rest API endpoint and return all open PRs.
        :param url: The URL to make the request to
        :return: List of PRs in dict / json
        """
        headers = {"Authorization": "token " + self.github_token}
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return (
            [response.json()] if isinstance(response.json(), dict) else response.json()
        )
