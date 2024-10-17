"""This test file covers all tests for the read_data module."""

from unittest.mock import patch, mock_open
from read_data import get_token, get_config


mock_config = """
---
maintainer: mock_maintainer
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
defaults:
  author: WX67YZ
  channel: CH12NN34
"""


def test_get_token():
    """This test checks that a value is returned when the function is called with a specific token."""
    with patch(
        "builtins.open", mock_open(read_data='{"mock_token_1": "mock_value_1"}')
    ):
        res = get_token("mock_token_1")
        assert res == "mock_value_1"


def test_get_user_map():
    """This test ensures that the JSON file is read and converted to a dictionary correctly."""
    with patch("builtins.open", mock_open(read_data=mock_config)):
        res = get_config("user-map")
        assert res == {
            "mock_user_1": "mock_id_1",
            "mock_user_2": "mock_id_2"
        }


def test_get_repos():
    """This test checks that a list is returned if a string list of repos is read with no comma at the end."""
    with patch("builtins.open", mock_open(read_data=mock_config)):
        res = get_config("repos")
        assert res == {
                "organisation1": ["repo1", "repo2"],
                "organisation2": ["repo1", "repo2"]
            }


def test_get_maintainer():
    """This test checks that the user's name is returned."""
    with patch("builtins.open", mock_open(read_data=mock_config)):
        res = get_config("maintainer")
        assert res == "mock_maintainer"
