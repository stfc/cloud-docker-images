import sys
from typing import Dict, List
import openstack
from openstack.identity.v3.project import Project
from cloudmon.utils import run_scrape, parse_args


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


def get_limits_for_project(instance: str, project_id) -> Dict:
    """
    Get limits for a project. This is currently using openstack-cli
    This will be rewritten to instead use openstacksdk
    :param instance: cloud we want to scrape from
    :param project_id: project id we want to collect limits for
    :return: a set of limit properties for project we want
    """
    conn = openstack.connect(instance)

    # Nova (Compute)
    nova_limits = conn.compute.get_limits(project=project_id).absolute
    # Cinder (Volumes)
    cinder_limits = conn.block_storage.get_limits(project=project_id).absolute
    # Neutron (Network)
    neutron_quotas = conn.network.get_quota(quota=project_id, details=True)

    return {
        **nova_limits,
        **cinder_limits,
        # get floating ip limits from neutron
        **{
            "floating_ips": neutron_quotas.floating_ips.get("limit", -1),
            "floating_ips_used": neutron_quotas.floating_ips.get("used", 0)
        }
    }


def is_valid_project(project: Project) -> bool:
    """
    helper function which returns if project is valid to get limits for
    :param project: project to check
    :return: boolean, True if project should be accounted for in limits
    """
    # we ignore rally and heat created projects because they are testing ones
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
