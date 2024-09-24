"""This test file covers all tests for the read_data module."""

from unittest.mock import patch, mock_open
from read_data import get_token, get_repos, get_user_map, get_maintainer


def test_get_token():
    """This test checks that a value is returned when the function is called with a specific token."""
    with patch(
        "builtins.open", mock_open(read_data='{"mock_token_1": "mock_value_1"}')
    ):
        res = get_token("mock_token_1")
        assert res == "mock_value_1"


def test_get_user_map():
    """This test ensures that the JSON file is read and converted to a dictionary correctly."""
    with patch("builtins.open", mock_open(read_data='{"mock_user_1": "mock_id_1"}')):
        res = get_user_map()
        assert res == {"mock_user_1": "mock_id_1"}


def test_get_repos():
    """This test checks that a list is returned if a string list of repos is read with no comma at the end."""
    with patch("builtins.open", mock_open(read_data="repo1,repo2")):
        res = get_repos()
        assert res == ["repo1", "repo2"]


def test_get_repos_trailing_separator():
    """
    This test checks that a list of repos is returned correctly if there is a trailing comma at the end of the list.
    """
    with patch("builtins.open", mock_open(read_data="repo1,repo2,")):
        res = get_repos()
        assert res == ["repo1", "repo2"]


def test_get_maintainer():
    """This test checks that the user's name is returned."""
    with patch("builtins.open", mock_open(read_data="mock_person")):
        res = get_maintainer()
        assert res == "mock_person"


def test_get_maintainer_no_value():
    """This test checks that the defualt user ID is returned if maintainer.txt is empty."""
    with patch("builtins.open", mock_open(read_data="")):
        res = get_maintainer()
        assert res == "U05RBU0RF4J"  # Default Maintainer: Kalibh Halford
