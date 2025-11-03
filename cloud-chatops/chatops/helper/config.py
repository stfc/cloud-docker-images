"""Module to load and retrieve the app config."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from helper.data import User


@dataclass
class GitHubConfig:
    """Class to store GitHub config data."""

    enabled: bool
    repositories: List[str]

    @classmethod
    def from_config(cls, config: Dict):
        """
        Create the class from the config file data.
        :param config: The GitHub config as a dict from the file.
        """
        enabled = config["enabled"]
        repos = []
        if enabled:
            r = config["repositories"]
            repos = []
            for owner in r:
                repos += [f"{owner}/{repo}" for repo in r[owner]]
        return cls(
            enabled=enabled,
            repositories=repos,
        )


@dataclass
class GitLabConfig:
    """Class to store GitLab config data."""

    enabled: bool
    domain: str
    projects: List[str]

    @classmethod
    def from_config(cls, config: Dict):
        """
        Create the class from the config file data.
        :param config: The GitLab config as a dict from the file.
        """
        enabled = config["enabled"]
        projects = []
        domain = ""
        if enabled:
            p = config["projects"]
            projects = []
            for group in p:
                projects += [f"{group}%2F{project}" for project in p[group]]
            domain = config["domain"]
        return cls(
            enabled=enabled,
            domain=domain,
            projects=projects,
        )


@dataclass
class Config:
    """Class to store app config at runtime."""

    users: List[User]
    github: GitHubConfig
    gitlab: GitLabConfig

    @classmethod
    def from_dict(cls, config: Dict):
        """
        Create the Config from a file.
        :param config: The app config as a dict from the file.
        """
        users = [User.from_config(user) for user in config["app"]["users"]]
        github = GitHubConfig.from_config(config["github"])
        gitlab = GitLabConfig.from_config(config["gitlab"])

        return cls(
            users=users,
            github=github,
            gitlab=gitlab,
        )


def load_config(path: Union[str, Path] = "") -> Config:
    """
    Reads the config file into the Config dataclass and returns it.
    :param path: Path to the config file
    :return: The config object
    """
    if not path:
        path = get_path() / "config.yml"
    with open(path, "r", encoding="utf-8") as file:
        _config = yaml.safe_load(file)
    return Config.from_dict(_config)


# pylint: disable=C0103
@dataclass
class Secrets:
    """Class to store secrets at runtime."""

    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: Optional[str] = ""
    SLACK_SIGNING_SECRET: Optional[str] = ""
    SCHEDULED_REMINDER_TOKEN: Optional[str] = ""
    GITHUB_TOKEN: Optional[str] = ""
    GITLAB_TOKEN: Optional[str] = ""


def load_secrets(path: Union[str, Path] = "") -> Secrets:
    """
    Read the secrets file and return the Secrets dataclass.
    :param path: Path to the secrets file
    :return: The secret object
    """
    if not path:
        path = get_path() / "secrets.yml"
    with open(path, "r", encoding="utf-8") as file:
        _secrets = yaml.safe_load(file)
    return Secrets(**_secrets)


def get_path() -> Path:
    """
    Determine which path to use for reading secrets.
    This differs between development and production environments.
    :return: The path as a string
    """
    if sys.argv[0].endswith("dev.py"):
        # Using dev secrets here for local testing as it runs the app.
        # in a separate Slack Workspace than the production app.
        # This means the slash commands won't be picked up by the production app.
        home_path = (
            os.environ.get("HOME", "")
            if os.environ.get("HOME", "")
            else os.environ.get("HOMEPATH", "")
        )
        if not home_path:
            raise RuntimeError(
                "Are you trying to run locally? Couldn't find HOME or HOMEPATH in your environment variables."
            )
        path = Path(home_path) / "dev_cloud_chatops"
        if not path.exists():
            raise RuntimeError(f"Could not find the path {path} on the system.")
        return path
    # Docker image path
    return Path("/usr/src/app/")
