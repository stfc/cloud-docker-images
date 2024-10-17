"""This module handles reading data from files such as secrets and user maps."""

from typing import List, Dict, Union
import sys
import os
import json
import yaml
from errors import (
    RepositoriesNotGiven,
    UserMapNotGiven,
    TokensNotGiven,
)

# Production secret path
PATH = "/usr/src/app/cloud_chatops_secrets/"
try:
    if sys.argv[1] == "local":
        # Using dev secrets here for local testing as it runs the application
        # in a separate Slack Workspace than the production application.
        # This means the slash commands won't be picked up by the production application.
        PATH = f"{os.environ['HOME']}/dev_cloud_chatops_secrets/"
except IndexError:
    pass
except KeyError:
    print(
        "Are you trying to run locally? Couldn't find HOME in your environment variables."
    )
    sys.exit()


def validate_required_files() -> None:
    """
    This function checks that all required files have data in them before the application runs.
    """
    repos = get_repos()
    if not repos:
        raise RepositoriesNotGiven("repos.csv does not contain any repositories.")

    tokens = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "GITHUB_TOKEN"]
    for token in tokens:
        temp = get_token(token)
        if not temp:
            raise TokensNotGiven(
                f"Token {token} does not have a value in secrets.json."
            )
    user_map = get_user_map()
    if not user_map:
        raise UserMapNotGiven("user_map.json is empty.")
    for item, value in user_map.items():
        if not value:
            raise UserMapNotGiven(f"User {item} does not have a Slack ID assigned.")


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
