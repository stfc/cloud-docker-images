import sys
from typing import List, Dict, Optional

from openstack import connect
from cloudMonitoring.utils import run_scrape, parse_args


def server_obj_to_len(server_obj) -> int:
    """
    Method that gets the length of a generator object
    :param server_obj: OpenStack generator object from a query
    :return: Integer for the length of the object i.e. number of results
    """
    generator_list = list(server_obj)
    total_results = len(generator_list)
    return total_results


def run_server_query(
    conn: connect,
    filters: Optional[Dict],
    page_size: int = 1000,
    call_limit: int = 1000,
) -> List:
    """
    Helper method for running server query using pagination - openstacksdk calls
    can only return a maximum number of values - (set by limit) and to continue getting values
    we need to run another call pass a "marker" value of the last
    item seen
    :param conn: OpenStack cloud connection
    :param filters: A dictionary of filters to run on the query (server-side)
    :param page_size: (Default 1000) how many items are returned by single call
    :param call_limit: (Default 1000) max number of paging iterations.
        - this is required to mitigate some bugs where successive paging loops back on itself
        leading to endless calls
    :return: A list of server objects
    """

    pagination_filters = {"limit": page_size, "marker": None}
    if not filters:
        filters = {}

    new_filters = {**filters, **pagination_filters}
    query_res = []

    curr_marker = None
    num_calls = 0
    while True:
        if num_calls > call_limit:
            break

        for i, server in enumerate(
            conn.compute.servers(details=False, all_projects=True, **new_filters)
        ):
            query_res.append(server)

            # openstacksdk calls break after going over pagination limit
            if i == page_size - 1:
                # restart the for loop with marker set
                new_filters.update({"marker": server["id"]})
                break

        # if marker hasn't changed, then has query terminated
        if new_filters["marker"] == curr_marker:
            break

        # set marker as current
        curr_marker = new_filters["marker"]
        num_calls += 1
    return query_res


def number_servers_total(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the total number of instances across
    all projects.
    :param conn: OpenStack cloud connection
    :returns: Number of VMs in total across the cloud
    """
    server_obj = run_server_query(conn, None)
    # get number of items in generator object
    total_instances = server_obj_to_len(server_obj)
    return total_instances


def number_servers_active(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    ACTIVE state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of active VMs
    """
    server_obj = run_server_query(conn, {"status": "ACTIVE"})
    # get number of items in generator object
    instance_active = server_obj_to_len(server_obj)
    return instance_active


def number_servers_build(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    BUILD state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in BUILD state
    """
    server_obj = run_server_query(conn, {"status": "BUILD"})
    # get number of items in generator object
    instance_build = server_obj_to_len(server_obj)
    return instance_build


def number_servers_error(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    ERROR state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in ERROR state
    """
    server_obj = run_server_query(conn, {"status": "ERROR"})
    # get number of items in generator object
    instance_err = server_obj_to_len(server_obj)
    return instance_err


def number_servers_shutoff(conn: connect) -> int:
    """
    Query an OpenStack Cloud to find the number of instances in
    SHUTOFF state.
    :param conn: OpenStack Cloud Connection
    :returns: Number of VMs in SHUTOFF (STOPPED) state
    """
    server_obj = run_server_query(conn, {"status": "SHUTOFF"})
    # get number of items in generator object
    instance_shutoff = server_obj_to_len(server_obj)
    return instance_shutoff


def get_all_server_statuses(cloud_name: str) -> str:
    """
    Collects the stats for vms and returns a dict
    :param cloud_name: Name of OpenStack cloud to connect to
    :return: A comma separated string containing VM states.
    """

    # connect to an OpenStack cloud
    conn = connect(cloud=cloud_name)
    # collect stats in order: total, active, build, error, shutoff
    total_vms = number_servers_total(conn)
    active_vms = number_servers_active(conn)
    build_vms = number_servers_build(conn)
    error_vms = number_servers_error(conn)
    shutoff_vms = number_servers_shutoff(conn)

    server_statuses = (
        f"VMStats,instance={cloud_name.capitalize()} "
        f"totalVM={total_vms}i,activeVM={active_vms}i,"
        f"buildVM={build_vms}i,errorVM={error_vms}i,"
        f"shutoffVM={shutoff_vms}i"
    )

    return server_statuses


def main(user_args: List):
    """
    Main method to collect server statuses for an influxDB instance
    """
    monitoring_args = parse_args(user_args, description="Get All VM Statuses")
    run_scrape(monitoring_args, get_all_server_statuses)


if __name__ == "__main__":
    main(sys.argv[1:])
