"""This test file covers all tests for the read_data module."""

from unittest.mock import patch, mock_open
import pytest
import yaml
from errors import RepositoriesNotGiven, TokensNotGiven, UserMapNotGiven
from read_data import get_token, get_config, validate_required_files


MOCK_CONFIG = """
---
user-map:
  mock_user_1: mock_id_1
  mock_user_2: mock_id_2
repos:
  organisation1:
    - repo1
    - repo2
  organisation2:
    - repo1
    - repo2
"""


def test_get_token_fails():
    """Test that an error is raised if trying to access a value that doesn't exist."""
    with patch(
        "builtins.open", mock_open(read_data='mock_token_1: mock_value_1')
    ):
        with pytest.raises(KeyError):
            get_token("mock_token_2")


def test_get_token():
    """This test checks that a value is returned when the function is called with a specific token."""
    with patch(
        "builtins.open", mock_open(read_data='mock_token_1: mock_value_1')
    ):
        res = get_token("mock_token_1")
        assert res == "mock_value_1"


def test_get_user_map():
    """This test ensures that the JSON file is read and converted to a dictionary correctly."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        res = get_config("user-map")
        assert res == {"mock_user_1": "mock_id_1", "mock_user_2": "mock_id_2"}


def test_get_repos():
    """This test checks that a list is returned if a string list of repos is read with no comma at the end."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        res = get_config("repos")
        assert res == {
            "organisation1": ["repo1", "repo2"],
            "organisation2": ["repo1", "repo2"],
        }


def test_get_config_fails():
    """This test checks that an error is raised when accessing a part of the config that doesn't exist."""
    with patch("builtins.open", mock_open(read_data=MOCK_CONFIG)):
        with pytest.raises(KeyError):
            get_config("unknown")


@patch("read_data.get_config")
@patch("read_data.get_token")
def test_validate_required_files(mock_get_token, mock_get_config):
    """Test the validate files function"""
    mock_get_token.side_effect = ["mock_bot", "mock_app", "mock_github"]
    mock_get_config.side_effect = [{"owner1": ["repo1"]}, {"github1": "slack1"}]
    validate_required_files()


@patch("read_data.get_config")
@patch("read_data.get_token")
def test_validate_required_files_fail_repo(mock_get_token, mock_get_config):
    """Test the validate files function"""
    mock_get_token.side_effect = ["mock_bot", "mock_app", "mock_github"]
    mock_get_config.side_effect = [{}, {"github1": "slack1"}]
    with pytest.raises(RepositoriesNotGiven):
        validate_required_files()


@patch("read_data.get_config")
@patch("read_data.get_token")
def test_validate_required_files_fail_token(mock_get_token, mock_get_config):
    """Test the validate files function"""
    mock_get_token.side_effect = ["", "mock_app", "mock_github"]
    mock_get_config.side_effect = [{"owner1": ["repo1"]}, {"github1": "slack1"}]
    with pytest.raises(TokensNotGiven):
        validate_required_files()


@patch("read_data.get_config")
@patch("read_data.get_token")
def test_validate_required_files_fail_user_map_slack(mock_get_token, mock_get_config):
    """Test the validate files function"""
    mock_get_token.side_effect = ["mock_bot", "mock_app", "mock_github"]
    mock_get_config.side_effect = [{"owner1": ["repo1"]}, {"github1": ""}]
    with pytest.raises(UserMapNotGiven) as exc:
        validate_required_files()
    assert str(exc.value) == "User github1 does not have a Slack ID assigned."


@patch("read_data.get_config")
@patch("read_data.get_token")
def test_validate_required_files_fail_user_map_github(mock_get_token, mock_get_config):
    """Test the validate files function"""
    mock_get_token.side_effect = ["mock_bot", "mock_app", "mock_github"]
    mock_get_config.side_effect = [{"owner1": ["repo1"]}, {"": "slack1"}]
    with pytest.raises(UserMapNotGiven) as exc:
        validate_required_files()
    assert (
        str(exc.value)
        == "Slack member slack1 does not have a GitHub username assigned."
    )


@patch("read_data.get_config")
@patch("read_data.get_token")
def test_validate_required_files_fail_user_map(mock_get_token, mock_get_config):
    """Test the validate files function"""
    mock_get_token.side_effect = ["mock_bot", "mock_app", "mock_github"]
    mock_get_config.side_effect = [{"owner1": ["repo1"]}, {}]
    with pytest.raises(UserMapNotGiven) as exc:
        validate_required_files()
    assert str(exc.value) == "config.yml does not contain a user map is empty."
