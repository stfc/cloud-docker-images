"""Tests for the validate_config module"""

from unittest.mock import MagicMock, patch

import pytest
from helper.exceptions import ErrorInConfig, ErrorInSecrets
from helper.validate_config import validate_required_files


# pylint:disable=too-many-positional-arguments,too-many-arguments
def make_mock_config(
    github_enabled=False,
    gitlab_enabled=False,
    users=True,
    github_repos=True,
    gitlab_domain=True,
    gitlab_projects=True,
):
    """Helper to make a mock config object with nested attributes."""
    config = MagicMock()
    config.github.enabled = github_enabled
    config.gitlab.enabled = gitlab_enabled
    config.users = users
    config.github.repositories = github_repos
    config.gitlab.domain = gitlab_domain
    config.gitlab.projects = gitlab_projects
    return config


def make_mock_secrets(
    slack_app_token=True,
    slack_signing_secret=True,
    slack_bot_token=True,
    github_token=True,
    gitlab_token=True,
):
    """Helper to make a mock secrets object."""
    secrets = MagicMock()
    secrets.SLACK_APP_TOKEN = slack_app_token
    secrets.SLACK_SIGNING_SECRET = slack_signing_secret
    secrets.SLACK_BOT_TOKEN = slack_bot_token
    secrets.GITHUB_TOKEN = github_token
    secrets.GITLAB_TOKEN = gitlab_token
    return secrets


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_dev_missing_app_token(mock_sys, mock_load_secrets, mock_load_config):
    """Test that missing SLACK_APP_TOKEN raises ErrorInSecrets in dev mode."""
    mock_sys.argv = ["dev.py"]
    mock_load_config.return_value = make_mock_config()
    mock_load_secrets.return_value = make_mock_secrets(slack_app_token=False)
    with pytest.raises(ErrorInSecrets, match="SLACK_APP_TOKEN"):
        validate_required_files()


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_main_missing_signing_secret(
    mock_sys, mock_load_secrets, mock_load_config
):
    """Test that missing SLACK_SIGNING_SECRET raises ErrorInSecrets in main mode."""
    mock_sys.argv = ["main.py"]
    mock_load_config.return_value = make_mock_config()
    mock_load_secrets.return_value = make_mock_secrets(slack_signing_secret=False)
    with pytest.raises(ErrorInSecrets, match="SLACK_SIGNING_SECRET"):
        validate_required_files()


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_missing_bot_token(mock_sys, mock_load_secrets, mock_load_config):
    """Test that missing SLACK_BOT_TOKEN raises ErrorInSecrets."""
    mock_sys.argv = ["main.py"]
    mock_load_config.return_value = make_mock_config()
    mock_load_secrets.return_value = make_mock_secrets(slack_bot_token=False)
    with pytest.raises(ErrorInSecrets, match="SLACK_BOT_TOKEN"):
        validate_required_files()


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_github_missing_token_or_repos(
    mock_sys, mock_load_secrets, mock_load_config
):
    """Test that missing GitHub token or repositories raise appropriate errors."""
    mock_sys.argv = ["main.py"]

    # Missing GITHUB_TOKEN
    config = make_mock_config(github_enabled=True)
    secrets = make_mock_secrets(github_token=False)
    mock_load_config.return_value = config
    mock_load_secrets.return_value = secrets
    with pytest.raises(ErrorInSecrets, match="GITHUB_TOKEN"):
        validate_required_files()

    # Missing repositories
    secrets = make_mock_secrets()
    config = make_mock_config(github_enabled=True, github_repos=False)
    mock_load_config.return_value = config
    mock_load_secrets.return_value = secrets
    with pytest.raises(ErrorInConfig, match="repositories"):
        validate_required_files()


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_gitlab_missing_fields(mock_sys, mock_load_secrets, mock_load_config):
    """Test that missing GitLab token, domain, or projects raise errors."""
    mock_sys.argv = ["main.py"]
    config = make_mock_config(gitlab_enabled=True)
    secrets = make_mock_secrets(gitlab_token=False)
    mock_load_config.return_value = config
    mock_load_secrets.return_value = secrets

    # Missing token
    with pytest.raises(ErrorInSecrets, match="GITLAB_TOKEN"):
        validate_required_files()

    # Missing domain
    config = make_mock_config(gitlab_enabled=True, gitlab_domain=False)
    secrets = make_mock_secrets()
    mock_load_config.return_value = config
    mock_load_secrets.return_value = secrets
    with pytest.raises(ErrorInConfig, match="domain"):
        validate_required_files()

    # Missing projects
    config = make_mock_config(gitlab_enabled=True, gitlab_projects=False)
    secrets = make_mock_secrets()
    mock_load_config.return_value = config
    mock_load_secrets.return_value = secrets
    with pytest.raises(ErrorInConfig, match="projects"):
        validate_required_files()


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_missing_users(mock_sys, mock_load_secrets, mock_load_config):
    """Test that missing users configuration raises ErrorInConfig."""
    mock_sys.argv = ["main.py"]
    mock_load_config.return_value = make_mock_config(users=False)
    mock_load_secrets.return_value = make_mock_secrets()
    with pytest.raises(ErrorInConfig, match="users"):
        validate_required_files()


@patch("helper.validate_config.load_config")
@patch("helper.validate_config.load_secrets")
@patch("helper.validate_config.sys")
def test_validate_all_good(mock_sys, mock_load_secrets, mock_load_config):
    """Test that validation passes successfully when all configs and secrets are valid."""
    mock_sys.argv = ["main.py"]
    mock_load_config.return_value = make_mock_config(
        github_enabled=True,
        gitlab_enabled=True,
    )
    mock_load_secrets.return_value = make_mock_secrets()
    # Should not raise anything
    validate_required_files()
