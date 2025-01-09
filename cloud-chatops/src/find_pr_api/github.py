"""This module finds all open pull requests from given repositories in GitHub."""

from typing import List, Dict
import requests
from helper.data import PR


class FindPRs:
    """This class finds all open pull requests in the given repositories. It can also sort them by property."""
    def run(self, repos: List, token: str) -> List[PR]:
        """
        Finds all open pull requests and returns them as a list of dataclasses.
        :param token: GitHub Personal Access Token
        :param repos: Dictionary of repository names and owners.
        :return: List of PRs
        """
        responses = []
        for repo in repos:
            responses += self.make_request(repo, token)

        return [PR.from_json(response) for response in responses]

    @staticmethod
    def make_request(repo: str, token: str) -> List[Dict]:
        """
        Send an HTTP request to the GitHub Rest API endpoint and return all open PRs.
        :param token: GitHub Personal Access Token
        :param repo: The repo to request. For example, stfc/cloud-docker-images
        :return: List of PRs in dict / json
        """
        headers = {"Authorization": "token " + token}
        url = f"https://api.github.com/repos/{repo}/pulls"
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return (
            [response.json()] if isinstance(response.json(), dict) else response.json()
        )

    @staticmethod
    def sort_by(obj_list: List[PR], prop: str, reverse: bool = False) -> List[PR]:
        """
        Sort the list of PR objects by property.
        :param obj_list: List of PRs
        :param prop: Property to sort by
        :param reverse: To sort in reverse
        :return: List of PRs
        """
        try:
            return sorted(obj_list, key=lambda pr: getattr(pr, prop), reverse=reverse)
        except AttributeError as exc:
            raise ValueError(f"Unable to sort list by {prop}") from exc

    @staticmethod
    def filter_by(obj_list: List[PR], prop: str, value: str) -> List[PR]:
        """
        Filter the list of PR object by property.
        :param obj_list: List of PR objects
        :param prop: Property to filter by
        :param value: Value to evaluate filter.
        :return: Filtered list of PRs.
        """
        try:
            return list(filter(lambda pr: getattr(pr, prop) == value, obj_list))
        except AttributeError as exc:
            raise ValueError(f"Unable to filter list by {prop}") from exc
