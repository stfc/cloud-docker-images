"""Module to load and retrieve the app config."""

import os
import sys

from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml

from helper.data import User

_CONFIG = None
_SECRETS = None


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


def load_config(path: str = None) -> Config:
    """
    Loads the config into global variables to be used by other modules.
    :param path: Path to the config file
    :return: The config object
    """
    if not path:
        path = get_path() + "config.yml"
    global _CONFIG  # pylint: disable=W0603
    if _CONFIG is None:
        with open(path, "r", encoding="utf-8") as file:
            __config = yaml.safe_load(file)
        _CONFIG = Config.from_dict(__config)
    return _CONFIG


def get_config():
    """
    Get the config from the global variables without loading it.
    """
    if _CONFIG is None:
        raise RuntimeError(
            "Configuration has not been loaded. Call load_config() first."
        )
    return _CONFIG


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


def load_secrets(path: str = None) -> Secrets:
    """
    Loads the secrets into global variables to be used by other modules.
    :param path: Path to the secrets file
    :return: The secret object
    """
    if not path:
        path = get_path() + "secrets.yml"
    global _SECRETS  # pylint: disable=W0603
    if _SECRETS is None:
        with open(path, "r", encoding="utf-8") as file:
            __secrets = yaml.safe_load(file)
        _SECRETS = Secrets(**__secrets)
    return _SECRETS


def get_secrets():
    """
    Get the secrets from the global variables without loading it.
    """
    if _SECRETS is None:
        raise RuntimeError("Secrets have not been loaded. Call load_secrets() first.")
    return _SECRETS


def get_path() -> str:
    """
    Determine which path to use for reading secrets.
    This differs between development and production environments.
    :return: The path as a string
    """
    if sys.argv[0].endswith("dev.py"):
        # Using dev secrets here for local testing as it runs the app.
        # in a separate Slack Workspace than the production app.
        # This means the slash commands won't be picked up by the production app.
        try:
            # Try multiple paths for Linux / Windows differences
            return f"{os.environ['HOME']}/dev_cloud_chatops/"
        except KeyError:
            try:
                return f"{os.environ['HOMEPATH']}\\dev_cloud_chatops\\"
            except KeyError as exc:
                raise RuntimeError(
                    "Are you trying to run locally? Couldn't find HOME or HOMEPATH in your environment variables."
                ) from exc

    # Docker image path
    return "/usr/src/app/"
