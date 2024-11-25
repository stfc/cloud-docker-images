"""
This module declares the dataclass used to store PR information.
This is preferred over dictionaries as dataclasses make code more readable.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict


@dataclass
class PR:
    """Class holding information about a single pull request."""

    # Disabling as we need more than 8 attributes
    # pylint: disable = R0902
    title: str
    author: str
    url: str
    created_at: datetime
    draft: bool
    stale: bool
    repository: str
    labels: List[str]

    @classmethod
    def from_json(cls, data: Dict):
        """
        Serialise the JSON data into this dataclass structure.
        :param data: JSON | Dict HTTP response data
        :return:
        """
        created_at = datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        return cls(
            title=f"{data['title']} #{data['number']}",
            author=data["user"]["login"],
            url=data["html_url"],
            stale=cls.is_stale(created_at),
            created_at=created_at,
            draft=data["draft"],
            labels=[label["name"] for label in data["labels"]],
            repository=data["html_url"].split(sep="/")[5],
        )

    @staticmethod
    def is_stale(created_at: datetime) -> bool:
        """
        Returns if a PR is stale or not.
        :param created_at: When the PR was created
        """
        opened_date = created_at.replace(tzinfo=None)
        datetime_now = datetime.now().replace(tzinfo=None)
        time_cutoff = datetime_now - timedelta(days=30)
        return opened_date <= time_cutoff
