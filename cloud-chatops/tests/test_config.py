"""This test file covers all tests for the config module."""

from unittest.mock import patch, mock_open
import pytest
from helper.config import (
    get_secrets,
    get_config,
    load_config,
    load_secrets,
    get_path,
)
from helper.data import User

MOCK_CONFIG = """
---
app:
  users:
    - realName: Real Name
      slackID: slack_id
      githubName: github_username
      gitlabName: gitlab_username


github:
  enabled: true
  repositories:
    owner1:
      - repo1
    owner2:
      - repo1

gitlab:
  enabled: true
  domain: gitlab.example.com
  projects:
    group1:
      - project1
    group2:
      - project1
"""

MOCK_SECRETS = """
---
SLACK_BOT_TOKEN: mock_slack_bot_token
SLACK_APP_TOKEN: mock_slack_app_token
SLACK_SIGNING_SECRET: mock_slack_signing_secret
SCHEDULED_REMINDER_TOKEN: mock_scheduled_reminder_token
GITHUB_TOKEN: mock_github_token
GITLAB_TOKEN: mock_gitlab_token
"""


def test_get_path_prod():
    """Test the production path is returned"""
    assert get_path() == "/usr/src/app/"


@patch("helper.config.os")
@patch("helper.config.sys")
def test_get_path_dev_linux(mock_sys, mock_os):
    """Test the development path is returned for a system using the HOME environment variable."""
    mock_sys.argv = ["dev.py"]
    mock_os.environ = {"HOME": "/home/mock"}
    assert get_path() == "/home/mock/dev_cloud_chatops/"


@patch("helper.config.os")
@patch("helper.config.sys")
def test_get_path_dev_windows(mock_sys, mock_os):
    """Test the development path is returned for a system using the HOMEPATH environment variable."""
    mock_sys.argv = ["dev.py"]
    mock_os.environ = {"HOMEPATH": "\\home\\mock"}
    assert get_path() == "\\home\\mock\\dev_cloud_chatops\\"


@patch("helper.config.os")
@patch("helper.config.sys")
def test_get_path_dev_fails(mock_sys, mock_os):
    """Test an error is raised if HOME or HOMEPATH can't be found in the environment."""
    mock_sys.argv = ["dev.py"]
    mock_os.environ = {}
    with pytest.raises(RuntimeError):
        get_path()


@patch("helper.config._CONFIG", None)
@patch("helper.config.get_path")
def test_load_config(mock_get_path):
    """Test the load_config function reads the mock config file and provides the data in the correct structure."""
    mock_get_path.return_value = "mock_path/"
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)) as mock_file:
        res = load_config()
    mock_get_path.assert_called_once_with()
    mock_file.assert_called_once_with("mock_path/config.yml", "r", encoding="utf-8")

    assert res.github.enabled is True
    assert res.github.repositories == ["owner1/repo1", "owner2/repo1"]
    assert res.gitlab.enabled is True
    assert res.gitlab.domain == "gitlab.example.com"
    assert res.gitlab.projects == ["group1%2Fproject1", "group2%2Fproject1"]
    assert res.users == [
        User(
            real_name="Real Name",
            slack_id="slack_id",
            github_name="github_username",
            gitlab_name="gitlab_username",
        )
    ]


@patch("helper.config._SECRETS", None)
@patch("helper.config.get_path")
def test_load_secrets(mock_get_path):
    """Test the load_secrets function reads the mock config file and provides the data in the correct structure."""
    mock_get_path.return_value = "mock_path/"
    with patch("builtins.open", mock_open(read_data=MOCK_SECRETS)) as mock_file:
        res = load_secrets()
    mock_get_path.assert_called_once_with()
    mock_file.assert_called_once_with("mock_path/secrets.yml", "r", encoding="utf-8")

    assert res.SLACK_BOT_TOKEN == "mock_slack_bot_token"
    assert res.SLACK_APP_TOKEN == "mock_slack_app_token"
    assert res.SLACK_SIGNING_SECRET == "mock_slack_signing_secret"
    assert res.SCHEDULED_REMINDER_TOKEN == "mock_scheduled_reminder_token"
    assert res.GITHUB_TOKEN == "mock_github_token"
    assert res.GITLAB_TOKEN == "mock_gitlab_token"


@patch("helper.config._SECRETS", None)
def test_get_secrets_fails():
    """Test an error is raised when secrets are not preloaded."""
    with pytest.raises(RuntimeError):
        get_secrets()


@patch("helper.config._SECRETS", True)
def test_get_secrets():
    """Test the global variable is returned."""
    assert get_secrets()


@patch("helper.config._CONFIG", None)
def test_get_config_fails():
    """Test an error is raised when the config is not preloaded."""
    with pytest.raises(RuntimeError):
        get_config()


@patch("helper.config._CONFIG", True)
def test_get_config():
    """Test the global variable is returned."""
    assert get_config()
