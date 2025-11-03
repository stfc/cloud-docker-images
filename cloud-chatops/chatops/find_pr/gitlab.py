"""This module finds all open merge requests from given projects in GitLab."""

from typing import List, Dict
import requests
from helper.data import PR
from helper.config import load_config


class GitLab:
    """This class finds all open merge requests in the given projects."""

    def __init__(self):
        """Initialise the class with the config."""
        self.config = load_config()

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

    def make_request(self, project: str, token: str) -> List[Dict]:
        """
        Send an HTTP request to the GitHub Rest API endpoint and return all open PRs.
        :param token: GitHub Personal Access Token
        :param project: URL encoded project path. Such as, stfc-cloud%2FSTFC-Cloud-Kayobe-Config
        :return: List of PRs in dict / json
        """
        headers = {"Authorization": "Bearer " + token}
        domain = self.config.gitlab.domain
        url = f"https://{domain}/api/v4/projects/{project}/merge_requests?state=opened&scope=all"
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        return (
            [response.json()] if isinstance(response.json(), dict) else response.json()
        )
