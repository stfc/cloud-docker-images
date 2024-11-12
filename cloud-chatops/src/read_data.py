"""This module handles reading data from files such as secrets and user maps."""

from typing import Dict, Union
import sys
import os
import json
import yaml
from errors import (
    RepositoriesNotGiven,
    UserMapNotGiven,
    TokensNotGiven,
    SecretsInPathNotFound,
)

# Production secret path
PATH = "/usr/src/app/cloud_chatops_secrets/"


if sys.argv[0].endswith("dev.py"):
    # Using dev secrets here for local testing as it runs the application
    # in a separate Slack Workspace than the production application.
    # This means the slash commands won't be picked up by the production application.
    try:
        # Try multiple paths for Linux / Windows differences
        PATH = f"{os.environ['HOME']}/dev_cloud_chatops_secrets/"
    except KeyError:
        try:
            PATH = f"{os.environ['HOMEPATH']}\\dev_cloud_chatops_secrets\\"
        except KeyError as exc:
            raise SecretsInPathNotFound(
                "Are you trying to run locally? Couldn't find HOME or HOMEPATH in your environment variables."
            ) from exc


def validate_required_files() -> None:
    """
    This function checks that all required files have data in them before the application runs.
    """
    repos = get_config("repos")
    if not repos:
        raise RepositoriesNotGiven("config.yml does not contain any repositories.")

    tokens = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "GITHUB_TOKEN"]
    for token in tokens:
        temp = get_token(token)
        if not temp:
            raise TokensNotGiven(
                f"Token {token} does not have a value in secrets.json."
            )
    user_map = get_config("user-map")
    if not user_map:
        raise UserMapNotGiven("config.yml does not contain a user map is empty.")
    for item, value in user_map.items():
        if not value:
            raise UserMapNotGiven(f"User {item} does not have a Slack ID assigned.")
        if not item:
            raise UserMapNotGiven(
                f"Slack member {value} does not have a GitHub username assigned."
            )


def get_token(secret: str) -> str:
    """
    This function will read from the secrets file and return a specified secret.
    :param secret: The secret to find
    :return: A secret as string
    """
    with open(PATH + "secrets.json", "r", encoding="utf-8") as file:
        data = file.read()
    secrets = json.loads(data)
    return secrets[secret]


def get_config(section: str = "all") -> Union[Dict, str]:
    """
    This function will return the specified section from the config file.
    :param section: The section of the config to retrieve.
    :return: The data retrieved from the config file.
    """
    with open(PATH + "config.yml", "r", encoding="utf-8") as config:
        config_data = yaml.safe_load(config)
    match section:
        case "all":
            return config_data
        case _:
            return config_data.get(section)
