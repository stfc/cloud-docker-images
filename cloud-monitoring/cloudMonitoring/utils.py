import configparser
from configparser import ConfigParser
from typing import Dict, Tuple, Callable
from pathlib import Path
import argparse
import requests


def read_config_file(config_filepath: Path) -> Dict:
    """
    This function reads a config file and puts it into a dictionary
    :param config_filepath:
    :return: A flattened dictionary containing key-value pairs from config file
    """
    config = ConfigParser()
    config.read(config_filepath)
    config_dict = {}
    for section in config.sections():
        for key, value in config.items(section):
            config_dict[f"{section}.{key}"] = value

    required_values = [
        "auth.password",
        "auth.username",
        "cloud.instance",
        "db.database",
        "db.host",
    ]
    assert all(
        val in config_dict for val in required_values
    ), "Config file is missing required values."
    return config_dict


def post_to_influxdb(
    data_string: str, host: str, db_name: str, auth: Tuple[str, str]
) -> None:
    """
    This function posts information to influxdb
    :param data_string: data to write
    :param host: hostname and port where influxdb can be accessed
    :param db_name: database name to write to
    :param auth: tuple of (username, password) to authenticate with influxdb
    """
    if not data_string:
        return

    url = f"http://{host}/write?db={db_name}&precision=s"
    response = requests.post(url, data=data_string, auth=auth, timeout=60)
    response.raise_for_status()


def parse_args(inp_args, description: str = "scrape metrics script") -> Dict:
    """
    This function parses influxdb args from a filepath passed into script when its run.
    The only thing the scripts takes as input is the path to the config file.
    :param description: The description of the script to print on help command
    :param inp_args: input arguments passed when a 'gather metrics' script is run
    :return: args from
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "config_filepath", type=Path, help="Path to influxdb config file"
    )
    try:
        args = parser.parse_args(inp_args)
    except argparse.ArgumentTypeError as exp:
        raise RuntimeError("Error reading input arguments") from exp

    if not args.config_filepath.is_file():
        raise RuntimeError(f"Invalid filepath given '{args.config_filepath}'")

    try:
        return read_config_file(args.config_filepath)
    except configparser.Error as exp:
        raise RuntimeError(
            f"could not read influxdb config file '{args.config_filepath}'"
        ) from exp


def run_scrape(influxdb_args, scrape_func: Callable[[str], str]):
    """
    run script to scrape info and post to influxdb
    :param influxdb_args: set of args passed in by user upon running script
    :param scrape_func: function to use to scrape info
    """
    scrape_res = scrape_func(influxdb_args["cloud.instance"])
    post_to_influxdb(
        scrape_res,
        host=influxdb_args["db.host"],
        db_name=influxdb_args["db.database"],
        auth=(influxdb_args["auth.username"], influxdb_args["auth.password"]),
    )
