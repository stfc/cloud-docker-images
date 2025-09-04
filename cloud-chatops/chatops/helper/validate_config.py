"""This module handles reading data from files such as secrets and user maps."""

import sys
from helper.exceptions import ErrorInConfig, ErrorInSecrets
from helper.config import get_config, get_secrets


def validate_required_files() -> None:
    """
    This function checks that the config.yaml and secrets.yaml are valid.
    """
    config = get_config()
    secrets = get_secrets()

    if sys.argv[0].endswith("dev.py") and not secrets.SLACK_APP_TOKEN:
        raise ErrorInSecrets("SLACK_APP_TOKEN")

    if sys.argv[0].endswith("main.py") and not secrets.SLACK_SIGNING_SECRET:
        raise ErrorInSecrets("SLACK_SIGNING_SECRET")

    if not secrets.SLACK_BOT_TOKEN:
        raise ErrorInSecrets("SLACK_BOT_TOKEN")

    if config.github.enabled:
        if not secrets.GITHUB_TOKEN:
            raise ErrorInSecrets("GITHUB_TOKEN")
        if not config.github.repositories:
            raise ErrorInConfig("github", "repositories")

    if config.gitlab.enabled:
        if not secrets.GITLAB_TOKEN:
            raise ErrorInSecrets("GITLAB_TOKEN")
        if not config.gitlab.domain:
            raise ErrorInConfig("gitlab", "domain")
        if not config.gitlab.projects:
            raise ErrorInConfig("gitlab", "projects")

    if not config.users:
        raise ErrorInConfig("app", "users")
