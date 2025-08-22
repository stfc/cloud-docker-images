import sys
from typing import Dict, List
import openstack
from openstack.compute.v2.service import Service
from openstack.network.v2.agent import Agent
from openstackquery import HypervisorQuery
from cloudMonitoring.utils import run_scrape, parse_args


def get_hypervisor_properties(hypervisor: Dict) -> Dict:
    """
    This function parses a dict returned by a HypervisorQuery to get properties in the correct format
    to feed into influxdb
    :param hypervisor: hypervisor to extract properties from
    :return: A dictionary of useful properties
    """
    hv_prop_dict = {
        "hv": {
            # this is populated by another command
            "aggregate": "no-aggregate",
            "memorymax": hypervisor["memory_mb_size"],
            "memoryused": hypervisor["memory_mb_used"],
            "memoryavailable": hypervisor["memory_mb_size"] - hypervisor["memory_mb_used"],
            "memperc": round(
                (hypervisor["memory_mb_used"] / hypervisor["memory_mb_size"]) * 100
            ),
            "cpumax": hypervisor["vcpus"],
            "cpuused": hypervisor["vcpus_used"],
            "cpuavailable": hypervisor["vcpus"] - hypervisor["vcpus_used"],
            "cpuperc": round((hypervisor["vcpus_used"] / hypervisor["vcpus"]) * 100),
            "agent": 1,
            "state": 1 if hypervisor["hypervisor_state"] == "up" else 0,
            "statetext": hypervisor["hypervisor_state"].capitalize(),
        }
    }
    hv_info = hv_prop_dict["hv"]

    hv_info["utilperc"] = max(hv_info["cpuperc"], hv_info["memperc"])
    hv_info["cpufull"] = 1 if hv_info["cpuperc"] >= 97 else 0
    hv_info["memfull"] = 1 if hv_info["memoryavailable"] <= 8192 else 0
    hv_info["full"] = int(hv_info["memfull"] or hv_info["cpufull"])

    return hv_prop_dict


def get_service_properties(service: Service) -> Dict:
    """
    This function parses a openstacksdk Service object to get properties in the correct format
    to feed into influxdb
    :param service: service to extract properties from
    :return: A dictionary of useful properties
    """
    service_prop_dict = {
        service["binary"]: {
            "agent": 1,
            "status": 1 if service["status"] == "enabled" else 0,
            "statustext": service["status"].capitalize(),
            "state": 1 if service["state"] == "up" else 0,
            "statetext": service["state"].capitalize(),
        }
    }
    return service_prop_dict


def get_agent_properties(agent: Agent) -> Dict:
    """
    This function parses a openstacksdk Agent object to get properties in the correct format
    to feed into influxdb
    :param agent: agent to extract properties from
    :return: A dictionary of useful properties
    """
    agent_prop_dict = {
        agent["binary"]: {
            "agent": 1,
            "state": 1 if agent["is_alive"] else 0,
            "statetext": "Up" if agent["is_alive"] else "Down",
            "status": 1 if agent["is_admin_state_up"] else 0,
            "statustext": "Enabled" if agent["is_admin_state_up"] else "Disabled",
        }
    }
    return agent_prop_dict


def convert_to_data_string(instance: str, service_details: Dict) -> str:
    """
    This function creates a data string from service properties to feed into influxdb
    :param instance: the cloud instance (prod or dev) that details were scraped from
    :param service_details: a set of service properties to parse
    :return: A data string of scraped info
    """
    data_string = ""
    for hypervisor_name, services in service_details.items():
        for service_binary, service_stats in services.items():
            statustext = service_stats.pop("statustext")
            statetext = service_stats.pop("statetext")
            new_data_string = (
                f"ServiceStatus"
                f',host="{hypervisor_name}"'
                f',service="{service_binary}"'
                f",instance={instance.capitalize()}"
                f',statetext="{statetext}"'
                f',statustext="{statustext}"'
            )

            aggregate = service_stats.pop("aggregate", None)
            if aggregate:
                new_data_string += f',aggregate="{aggregate}"'

            new_data_string += f" {get_service_prop_string(service_stats)}\n"
            data_string += new_data_string

    return data_string


def get_service_prop_string(service_dict: Dict) -> str:
    """
    This function is a helper function that creates a partial data string of just the
    properties scraped for a single service
    :param service_dict: properties scraped for a single service
    :return: a data string of scraped info
    """
    stats_strings = []
    for stat, val in service_dict.items():
        stats_strings.append(f"{stat}={val}i")
    return ",".join(stats_strings)


def get_all_hv_details(conn) -> Dict:
    """
    Get all hypervisor status information from openstack
    :param conn: openstack connection object
    :return: a dictionary of hypervisor status information
    """
    hv_details = {}

    hv_query = HypervisorQuery()
    hv_query.select_all()
    hv_query.run(conn.config.name)
    for hv in hv_query.to_props():
        hv_details[hv["hypervisor_name"]] = get_hypervisor_properties(hv)

    # populate found hypervisors with what aggregate they belong to - so we can filter by aggregate in grafana
    for aggregate in conn.compute.aggregates():
        for host_name in aggregate["hosts"]:
            if host_name in hv_details:
                hv_details[host_name]["hv"]["aggregate"] = aggregate["name"]
    return hv_details


def update_with_service_statuses(conn, status_details: Dict) -> Dict:
    """
    update status details with service status information from openstack
    :param conn: openstack connection object
    :param status_details: status details dictionary to update
    :return: a dictionary of updated status information with service statuses
    """
    for service in conn.compute.services():
        if service["host"] not in status_details.keys():
            status_details[service["host"]] = {}

        service_host = status_details[service["host"]]
        service_host.update(get_service_properties(service))
        if "hv" in service_host and service["binary"] == "nova-compute":
            service_host["hv"]["status"] = service_host["nova-compute"]["status"]
            service_host["hv"]["statustext"] = service_host["nova-compute"][
                "statustext"
            ]

    return status_details


def update_with_agent_statuses(conn, status_details: Dict) -> Dict:
    """
    update status details with network agent status information from openstack
    :param conn: openstack connection object
    :param status_details: status details dictionary to update
    :return: a dictionary of updated status information with network agent statuses
    """
    for agent in conn.network.agents():
        if agent["host"] not in status_details.keys():
            status_details[agent["host"]] = {}

        status_details[agent["host"]].update(get_agent_properties(agent))

    return status_details


def get_all_service_statuses(instance: str) -> str:
    """
    This function gets status information for each service node, hypervisor and network
    agent in openstack.
    :param instance: which cloud to scrape from (prod or dev)
    :return: A data string of scraped info
    """
    conn = openstack.connect(instance)
    all_details = get_all_hv_details(conn)
    all_details = update_with_service_statuses(conn, all_details)
    all_details = update_with_agent_statuses(conn, all_details)
    return convert_to_data_string(instance, all_details)


def main(user_args: List):
    """
    send service status info to influx
    :param user_args: args passed into script by user
    """
    influxdb_args = parse_args(user_args, description="Get All Service Statuses")
    run_scrape(influxdb_args, get_all_service_statuses)


if __name__ == "__main__":
    main(sys.argv[1:])
