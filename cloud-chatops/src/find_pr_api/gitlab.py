"""This module finds all open merge requests from given projects in GitLab."""

from typing import List, Dict
import requests
from helper.data import PR
from helper.read_config import get_config


class FindPRs:
    """This class finds all open merge requests in the given projects."""

    def run(self, projects: List, token: str) -> List[PR]:
        """
        Finds all open merge requests and returns them as a list of dataclasses.
        :param token: GitLab Personal Access Token
        :param projects: List of URL encoded project paths.
        :return: List of PRs
        """
        responses = []
        for project in projects:
            responses += self.make_request(project, token)

        return [PR.from_gitlab(response) for response in responses]

    @staticmethod
    def make_request(project: str, token: str) -> List[Dict]:
        """
        Send an HTTP request to the GitHub Rest API endpoint and return all open PRs.
        :param token: GitHub Personal Access Token
        :param project: URL encoded project path. Such as, stfc-cloud%2FSTFC-Cloud-Kayobe-Config
        :return: List of PRs in dict / json
        """
        headers = {"Authorization": "Bearer " + token}
        domain = get_config("gitlab_domain")
        url = f"https://{domain}/api/v4/projects/{project}/merge_requests?state=opened&scope=all"
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return (
            [response.json()] if isinstance(response.json(), dict) else response.json()
        )
