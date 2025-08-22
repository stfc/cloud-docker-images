import configparser
from pathlib import Path
from unittest.mock import patch, call, NonCallableMock, MagicMock

import pytest

from cloudMonitoring.utils import (
    read_config_file,
    post_to_influxdb,
    parse_args,
    run_scrape,
)


@patch("cloudMonitoring.utils.ConfigParser")
def test_read_config_file_valid(mock_config_parser):
    """
    tests read_config_file function when given a valid config file
    """
    mock_config_obj = mock_config_parser.return_value
    mock_config_obj.sections.return_value = ["auth", "cloud", "db"]
    mock_config_obj.items.side_effect = [
        [("password", "pass"), ("username", "user")],
        [("instance", "prod")],
        [("database", "cloud"), ("host", "localhost:8086")],
    ]
    mock_filepath = NonCallableMock()
    res = read_config_file(mock_filepath)
    mock_config_parser.assert_called_once()
    mock_config_obj.sections.assert_called_once()
    mock_config_obj.items.assert_has_calls([call("auth"), call("cloud"), call("db")])

    assert res == {
        "auth.password": "pass",
        "auth.username": "user",
        "cloud.instance": "prod",
        "db.database": "cloud",
        "db.host": "localhost:8086",
    }


@patch("cloudMonitoring.utils.ConfigParser")
def test_read_config_file_empty(mock_config_parser):
    """
    tests read_config_file function when given a emtpy config file
    """
    mock_config_parser.return_value.sections.return_value = []
    with pytest.raises(AssertionError):
        read_config_file(NonCallableMock())


@patch("cloudMonitoring.utils.requests")
def test_post_to_influxdb_valid(mock_requests):
    """
    tests post_to_influxdb function uses requests.post to post data correctly
    """
    mock_data_string = NonCallableMock()
    mock_host = "localhost:8086"
    mock_db_name = "cloud"
    mock_pass = NonCallableMock()
    mock_user = NonCallableMock()

    post_to_influxdb(mock_data_string, mock_host, mock_db_name, (mock_user, mock_pass))
    mock_requests.post.assert_called_once_with(
        "http://localhost:8086/write?db=cloud&precision=s",
        data=mock_data_string,
        auth=(mock_user, mock_pass),
        timeout=60,
    )
    mock_response = mock_requests.post.return_value
    mock_response.raise_for_status.assert_called_once()


@patch("cloudMonitoring.utils.requests")
def test_post_to_influxdb_empty_string(mock_requests):
    """
    tests post_to_influxdb function when datastring is empty, should do nothing
    """
    post_to_influxdb(
        "", NonCallableMock(), NonCallableMock(), (NonCallableMock(), NonCallableMock())
    )
    mock_requests.post.assert_not_called()


@patch("cloudMonitoring.utils.read_config_file")
def test_parse_args_valid_args(mock_read_config_file):
    """
    tests parse_args function with a valid filepath
    """
    test_dir = Path(__file__).parent
    package_root = test_dir.parent

    res = parse_args([f"{package_root}/configs/influxdb.conf"])
    assert res == mock_read_config_file.return_value


def test_parse_args_filepath_does_not_exist():
    """
    tests parse_args function with invalid filepath (doesn't exist)
    """
    with pytest.raises(RuntimeError):
        parse_args(["./invalid-filepath"])


def test_parse_args_filepath_invalid_dir_fp():
    """
    tests parse_args function with invalid filepath (points to directory)
    """
    with pytest.raises(RuntimeError):
        parse_args(["."])


@patch("cloudMonitoring.utils.read_config_file")
def test_parse_args_filepath_read_config_fails(mock_read_config_file):
    """
    tests parse_args function fails when read_config_file returns config error
    """
    mock_read_config_file.side_effect = configparser.Error

    test_dir = Path(__file__).parent
    package_root = test_dir.parent

    # Build path to the config file
    config_file = package_root / "configs" / "influxdb.conf"

    with pytest.raises(RuntimeError):
        parse_args([str(config_file)])

    mock_read_config_file.assert_called_once_with(config_file)


@patch("cloudMonitoring.utils.post_to_influxdb")
def test_run_scrape(mock_post_to_influxdb):
    """
    Tests run_scrape function.
    """
    mock_pass = NonCallableMock()
    mock_user = NonCallableMock()
    mock_host = NonCallableMock()
    mock_db = NonCallableMock()
    mock_instance = NonCallableMock()

    mock_influxdb_args = {
        "auth.password": mock_pass,
        "auth.username": mock_user,
        "cloud.instance": mock_instance,
        "db.database": mock_db,
        "db.host": mock_host,
    }
    mock_scrape_func = MagicMock()

    run_scrape(mock_influxdb_args, mock_scrape_func)
    mock_post_to_influxdb.assert_called_once_with(
        mock_scrape_func.return_value,
        host=mock_host,
        db_name=mock_db,
        auth=(mock_user, mock_pass),
    )
