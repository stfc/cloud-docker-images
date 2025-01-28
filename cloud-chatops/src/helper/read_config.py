"""This module handles reading data from files such as secrets and user maps."""

from typing import Dict, Union, List
import sys
import os
import yaml
from helper.errors import ErrorInConfig, ErrorInSecrets
from helper.data import User


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
    return "/usr/src/app/cloud_chatops/"


def get_token(secret: str) -> str:
    """
    This function reads from the secrets file and returns a specified secret.
    :param secret: The secret to find
    :return: The secret as string
    """
    path = get_path()
    with open(path + "secrets/secrets.yml", "r", encoding="utf-8") as secrets:
        secrets_data = yaml.safe_load(secrets)
        return secrets_data[secret]


def get_config(section: str) -> Union[List, Dict, str]:
    """
    This function returns the specified section from the config file.
    :param section: The section of the config to retrieve.
    :return: The data retrieved from the config file.
    """
    path = get_path()
    with open(path + "config/config.yml", "r", encoding="utf-8") as config:
        config_data = yaml.safe_load(config)
    match section:
        case "users":
            return [User.from_config(user) for user in config_data["app"]["users"]]
        case "repos":
            data = config_data["github"]["repositories"]
            repos = []
            for owner in data:
                repos += [f"{owner}/{repo}" for repo in data[owner]]
            return repos
        case "gitlab_domain":
            return config_data["gitlab"]["domain"]
        case "projects":
            data = config_data["gitlab"]["projects"]
            projects = []
            for group in data:
                projects += [f"{group}%2F{project}" for project in data[group]]
            return projects
        case _:
            raise KeyError(f"No section in config.yml named {section}.")


def validate_required_files() -> None:
    """
    This function checks that the config.yaml and secrets.yaml are valid.
    """
    if sys.argv[0].endswith("dev.py") and not get_token("SLACK_APP_TOKEN"):
        raise ErrorInSecrets("SLACK_APP_TOKEN")

    if sys.argv[0].endswith("main.py") and not get_token("SLACK_SIGNING_SECRET"):
        raise ErrorInSecrets("SLACK_SIGNING_SECRET")

    if not get_token("SLACK_BOT_TOKEN"):
        raise ErrorInSecrets("SLACK_BOT_TOKEN")

    github_config = get_config("github")
    if github_config["enabled"]:
        if not get_token("GITHUB_TOKEN"):
            raise ErrorInSecrets("GITHUB_TOKEN")
        if not github_config["repositories"]:
            raise ErrorInConfig("github", "repositories")

    gitlab_config = get_config("gitlab")
    if gitlab_config["enabled"]:
        if not get_token("GITLAB_TOKEN"):
            raise ErrorInSecrets("GITLAB_TOKEN")
        if not gitlab_config["domain"]:
            raise ErrorInConfig("gitlab", "domain")
        if not gitlab_config["projects"]:
            raise ErrorInConfig("gitlab", "projects")

    app_config = get_config("app")
    if not app_config["users"]:
        raise ErrorInConfig("app", "users")
