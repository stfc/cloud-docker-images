"""Tests for data.py"""

from datetime import datetime, timedelta
from helper.data import PR, User

# pylint: disable=R0801


MOCK_GITHUB_DATA = {
    "title": "mock_title",
    "number": 1,
    "user": {"login": "mock_author"},
    "html_url": "https://api.github.com/repos/mock_owner/mock_repo/pulls",
    "created_at": "2024-11-15T07:33:56Z",
    "draft": False,
    "labels": [{"name": "mock_label"}],
}

MOCK_PR = PR(
    title="mock_title #1",
    author="mock_author",
    url="https://api.github.com/repos/mock_owner/mock_repo/pulls",
    stale=True,
    draft=False,
    labels=["mock_label"],
    repository="mock_repo",
    created_at=datetime.strptime("2024-11-15T07:33:56Z", "%Y-%m-%dT%H:%M:%SZ"),
)

MOCK_GITLAB_DATA = {
    "title": "mock_title",
    "iid": 1,
    "author": {"username": "mock-user"},
    "web_url": "https://gitlab.stfc.ac.uk/mock-group/mock-project/-/merge_requests/205",
    "created_at": "2024-12-15T07:33:56.000+00:00",
    "draft": False,
    "labels": ["mock_label"],
}

MOCK_MR = PR(
    title="mock_title #1",
    author="mock-user",
    url="https://gitlab.stfc.ac.uk/mock-group/mock-project/-/merge_requests/205",
    stale=True,
    draft=False,
    labels=["mock_label"],
    repository="mock-project",
    created_at=datetime.fromisoformat("2024-12-15T07:33:56.000+00:00"),
    )

MOCK_USER = User(
    real_name="mock user", github_name="mock_github", slack_id="mock_slack"
)

# pylint: disable=R0801


def test_is_stale_false():
    """Test that is_stale returns false for a PR less than 30 days old."""
    assert not PR.is_stale(datetime.now())


def test_is_stale_true():
    """Test that is_stale returns false for a PR 30 days or older."""
    assert PR.is_stale(datetime.now() - timedelta(days=30))


def test_from_github():
    """Test that the JSON | Dict data is correctly serialised into a dataclass."""
    assert MOCK_PR == PR.from_github(MOCK_GITHUB_DATA)


def test_from_gitlab():
    """Test that the JSON | Dict data is correctly serialised into a dataclass."""
    assert MOCK_MR == PR.from_gitlab(MOCK_GITLAB_DATA)


def test_from_config():
    """Test that the User object is returned when supplied with info from the config."""
    mock_data = {
        "real_name": "mock user",
        "github_name": "mock_github",
        "slack_id": "mock_slack",
    }
    assert MOCK_USER == User.from_config(mock_data)
