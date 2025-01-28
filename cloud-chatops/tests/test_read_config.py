"""This test file covers all tests for the read_config module."""

from unittest.mock import patch, mock_open
import pytest
from helper.data import User
from helper.errors import ErrorInConfig, ErrorInSecrets
from helper.read_config import get_token, get_config, validate_required_files, get_path

MOCK_CONFIG = """
---
app:
  users:
    - real_name: Real Name
      slack_id: slack_id
      github_name: github_username
      gitlab_name: gitlab_username


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

MOCK_USER = User(
    real_name="Real Name", github_name="github_username", slack_id="slack_id", gitlab_name="gitlab_username"
)


def test_get_path_prod():
    """Test the production path is returned"""
    assert get_path() == "/usr/src/app/cloud_chatops/"


@patch("helper.read_config.os")
@patch("helper.read_config.sys")
def test_get_path_dev_linux(mock_sys, mock_os):
    """Test the development path is returned for a system using the HOME environment variable."""
    mock_sys.argv = ["dev.py"]
    mock_os.environ = {"HOME": "/home/mock"}
    assert get_path() == "/home/mock/dev_cloud_chatops/"


@patch("helper.read_config.os")
@patch("helper.read_config.sys")
def test_get_path_dev_windows(mock_sys, mock_os):
    """Test the development path is returned for a system using the HOMEPATH environment variable."""
    mock_sys.argv = ["dev.py"]
    mock_os.environ = {"HOMEPATH": "\\home\\mock"}
    assert get_path() == "\\home\\mock\\dev_cloud_chatops\\"


@patch("helper.read_config.os")
@patch("helper.read_config.sys")
def test_get_path_dev_fails(mock_sys, mock_os):
    """Test an error is raised if HOME or HOMEPATH can't be found in the environment."""
    mock_sys.argv = ["dev.py"]
    mock_os.environ = {}
    with pytest.raises(RuntimeError):
        get_path()


def test_get_token_fails():
    """Test that an error is raised if trying to access a value that doesn't exist."""
    with patch("builtins.open", mock_open(read_data="mock_token_1: mock_value_1")):
        with pytest.raises(KeyError):
            get_token("mock_token_2")


def test_get_token():
    """This test checks that a value is returned when the function is called with a specific token."""
    with patch("builtins.open", mock_open(read_data="mock_token_1: mock_value_1")):
        res = get_token("mock_token_1")
    assert res == "mock_value_1"


def test_get_config_users():
    """This test ensures that a list of User objects is returned from the config."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        res = get_config("users")
        assert res == [MOCK_USER]


def test_get_config_repos():
    """This test checks that the repos are read and formatted correctly."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        res = get_config("repos")
        assert res == [
            "owner1/repo1",
            "owner2/repo1",
        ]


def test_get_config_projects():
    """This test checks that the projects are read and formatted correctly."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        res = get_config("projects")
        assert res == ["group1%2Fproject1", "group2%2Fproject1"]


def test_get_config_gitlab_domain():
    """Tests that the GitLab domain is returned from the config."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        res = get_config("gitlab_domain")
        assert res == "gitlab.example.com"


def test_get_config_fails():
    """This test checks that an error is raised when accessing a part of the config that doesn't exist."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        with pytest.raises(KeyError):
            get_config("unknown")


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_dev(mock_get_token, mock_get_config):
    """Test the validate files function passes when running through dev.py."""
    mock_get_token.return_value = "mock_token"
    mock_get_config.side_effect = [{"enabled": False}, {"enabled": False}, {"users": ["mock_users"]}]
    with patch("sys.argv", ["dev.py"]):
        validate_required_files()


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_main(mock_get_token, mock_get_config):
    """Test the validate files function passes when running through dev.py."""
    mock_get_token.return_value = "mock_token"
    mock_get_config.side_effect = [{"enabled": False}, {"enabled": False}, {"users": ["mock_users"]}]
    with patch("sys.argv", ["main.py"]):
        validate_required_files()


@patch("helper.read_config.get_token")
def test_validate_required_files_dev_fails(mock_get_token):
    """Test the validate files function fails when running through dev.py."""
    mock_get_token.return_value = ""
    with patch("sys.argv", ["dev.py"]):
        with pytest.raises(ErrorInSecrets) as exc:
            validate_required_files()
        assert exc.value.args[0] == "There is a problem with your secrets.yaml. The secret SLACK_APP_TOKEN is not set."


@patch("helper.read_config.get_token")
def test_validate_required_files_main_fails(mock_get_token):
    """Test the validate files function fails when running through main.py."""
    mock_get_token.return_value = ""
    with patch("sys.argv", ["main.py"]):
        with pytest.raises(ErrorInSecrets) as exc:
            validate_required_files()
        assert exc.value.args[0] == "There is a problem with your secrets.yaml. The secret SLACK_SIGNING_SECRET is not set."


@patch("helper.read_config.get_token")
def test_validate_required_files_fail_slack_bot_token(mock_get_token):
    """Test the validate files function fails when the Slack bot token is not given."""
    mock_get_token.return_value = ""
    with pytest.raises(ErrorInSecrets) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your secrets.yaml. The secret SLACK_BOT_TOKEN is not set."


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_github_token_fails(mock_get_token, mock_get_config):
    """Test the validate files function fails when the GitHub token is not given."""
    mock_get_config.return_value = {"enabled": True}
    mock_get_token.side_effect = ["mock_slack_bot_token", ""]
    with pytest.raises(ErrorInSecrets) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your secrets.yaml. The secret GITHUB_TOKEN is not set."


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_github_repositories_fails(mock_get_token, mock_get_config):
    """Test the validate files function fails when GitHub repositories are not given."""
    mock_get_config.return_value = {
        "enabled": True,
        "repositories": {}
    }
    mock_get_token.side_effect = ["mock_slack_bot_token", "mock_github_token"]
    with pytest.raises(ErrorInConfig) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your config.yaml. The feature github does not have the parameter repositories set."


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_gitlab_token_fails(mock_get_token, mock_get_config):
    """Test the validate files function fails when the GitLab token is not given."""
    mock_get_config.side_effect = [{"enabled": False}, {"enabled": True}]
    mock_get_token.side_effect = ["mock_slack_bot_token", ""]
    with pytest.raises(ErrorInSecrets) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your secrets.yaml. The secret GITLAB_TOKEN is not set."


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_gitlab_domain_fails(mock_get_token, mock_get_config):
    """Test the validate files function fails when the GitLab domain is not given."""
    mock_get_config.side_effect = [
        {"enabled": False},
        {
            "enabled": True,
            "domain": "",
            "projects": {}
        }
    ]
    mock_get_token.side_effect = ["mock_slack_bot_token", "mock_github_token", "mock_gitlab_token"]
    with pytest.raises(ErrorInConfig) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your config.yaml. The feature gitlab does not have the parameter domain set."


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_gitlab_projects_fails(mock_get_token, mock_get_config):
    """Test the validate files function fails when GitLab projects are not given."""
    mock_get_config.side_effect = [
        {"enabled": False},
        {
            "enabled": True,
            "domain": "gitlab.example.com",
            "projects": {}
         }
    ]
    mock_get_token.side_effect = ["mock_slack_bot_token", "mock_github_token", "mock_gitlab_token"]
    with pytest.raises(ErrorInConfig) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your config.yaml. The feature gitlab does not have the parameter projects set."


@patch("helper.read_config.get_config")
@patch("helper.read_config.get_token")
def test_validate_required_files_app_users_fails(mock_get_token, mock_get_config):
    """Test the validate files function fails when the GitLab token is not given."""
    mock_get_config.side_effect = [{"enabled": False}, {"enabled": False}, {"users": []}]
    mock_get_token.side_effect = ["mock_slack_bot_token"]
    with pytest.raises(ErrorInConfig) as exc:
        validate_required_files()
    assert exc.value.args[0] == "There is a problem with your config.yaml. The feature app does not have the parameter users set."
