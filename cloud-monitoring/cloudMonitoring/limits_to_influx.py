import sys
from typing import Dict, List
import openstack
from openstack.identity.v3.project import Project
from cloudMonitoring.utils import run_scrape, parse_args


def convert_to_data_string(instance: str, limit_details: Dict) -> str:
    """
    converts a dictionary of values into a data-string influxdb can read
    :param instance: which cloud the info was scraped from (prod or dev)
    :param limit_details: a dictionary of values to convert to string
    :return: a comma-separated string of key=value taken from input dictionary
    """
    data_string = ""
    for project_name, limit_entry in limit_details.items():
        parsed_project_name = project_name.replace(" ", "\ ")
        data_string += (
            f'Limits,Project="{parsed_project_name}",'
            f"instance={instance.capitalize()} "
            f"{get_limit_prop_string(limit_entry)}\n"
        )
    return data_string


def get_limit_prop_string(limit_details):
    """
    This function is a helper function that creates a partial data string of just the
    properties scraped for a single service
    :param limit_details: properties scraped for a single project
    :return: a data string of scraped info
    """
    # all limit properties are integers so add 'i' for each value
    limit_strings = []
    for limit, val in limit_details.items():
        limit_strings.append(f"{limit}={val}i")
    return ",".join(limit_strings)


def extract_limits(limits_dict) -> Dict:
    """
    helper function to get info from
    :param limits_dict: a dictionary of project limits to extract useful properties from
    :return: a dictionary of useful properties with keys that match expected keys in influxdb
    """
    # the keys need changing to match legacy data when we used the openstack-cli
    mappings = {
        "server_meta": "maxServerMeta",
        "personality": "maxPersonality",
        "server_groups_used": "totalServerGroupsUsed",
        "image_meta": "maxImageMeta",
        "personality_size": "maxPersonalitySize",
        "keypairs": "maxTotalKeypairs",
        "security_group_rules": "maxSecurityGroupRules",
        "server_groups": "maxServerGroups",
        "total_cores_used": "totalCoresUsed",
        "total_ram_used": "totalRAMUsed",
        "instances_used": "totalInstancesUsed",
        "security_groups": "maxSecurityGroups",
        "floating_ips_used": "totalFloatingIpsUsed",
        "total_cores": "maxTotalCores",
        "server_group_members": "maxServerGroupMembers",
        "floating_ips": "maxTotalFloatingIps",
        "security_groups_used": "totalSecurityGroupsUsed",
        "instances": "maxTotalInstances",
        "total_ram": "maxTotalRAMSize",
    }
    parsed_limits = {}
    for key, val in mappings.items():
        try:
            parsed_limits[val] = limits_dict[key]
        except KeyError as exp:
            raise RuntimeError(f"could not find {key} in project limits") from exp
    return parsed_limits


def get_limits_for_project(instance: str, project_id) -> Dict:
    """
    Get limits for a project. This is currently using openstack-cli
    This will be rewritten to instead use openstacksdk
    :param instance: cloud we want to scrape from
    :param project_id: project id we want to collect limits for
    :return: a set of limit properties for project we want
    """
    conn = openstack.connect(instance)
    project_details = {
        **extract_limits(conn.get_compute_limits(project_id)),
        **conn.get_volume_limits(project_id)["absolute"],
    }
    return project_details


def is_valid_project(project: Project) -> bool:
    """
    helper function which returns if project is valid to get limits for
    :param project: project to check
    :return: boolean, True if project should be accounted for in limits
    """
    invalid_strings = ["_rally", "844"]
    return all(string not in project["name"] for string in invalid_strings)


def get_all_limits(instance: str) -> str:
    """
    This function gets limits for each project on openstack
    :param instance: which cloud to scrape from (prod or dev)
    :return: A data string of scraped info
    """
    conn = openstack.connect(cloud=instance)
    limit_details = {}
    for project in conn.list_projects():
        if is_valid_project(project):
            limit_details[project["name"]] = get_limits_for_project(
                instance, project["id"]
            )
    return convert_to_data_string(instance, limit_details)


def main(user_args: List):
    """
    send limits to influx
    :param user_args: args passed into script by user
    """
    monitoring_args = parse_args(user_args, description="Get All Project Limits")
    run_scrape(monitoring_args, get_all_limits)


if __name__ == "__main__":
    main(sys.argv[1:])
