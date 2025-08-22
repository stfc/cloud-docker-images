import sys
from typing import List, Dict
import openstack
from cloudMonitoring.structs.slottifier_entry import SlottifierEntry
from cloudMonitoring.utils import parse_args, run_scrape
from openstackquery import HypervisorQuery


def get_hv_info(hypervisor: Dict, aggregate_info: Dict, service_info: Dict) -> Dict:
    """
    Helper function to get hv information on vcpus/memory available
    :param hypervisor: a dictionary holding info on hypervisor
    :param aggregate_info: a dictionary holding info on aggregate hypervisor belongs to
    :param service_info: a dictionary holding info on nova compute service running on hypervisor
    :return: a dictionary of vcpus/memory available for given hv
    """
    hv_info = {
        "vcpus_available": 0,
        "mem_available": 0,
        "gpu_capacity": 0,
        "vcpus_capacity": 0,
        "mem_capacity": 0,
        "compute_service_status": "disabled",
    }

    vcpus = hypervisor.get("hypervisor_vcpus", "0")
    vcpus_used = hypervisor.get("hypervisor_vcpus_used", "0")

    # Only convert to int if the value is not 'Not Found'
    if vcpus != "Not Found":
        vcpus = int(vcpus)
    else:
        vcpus = 0

    if vcpus_used != "Not Found":
        vcpus_used = int(vcpus_used)
    else:
        vcpus_used = 0

    memory_size = hypervisor.get("hypervisor_memory_size", "0")
    memory_used = hypervisor.get("hypervisor_memory_used", "0")

    if memory_size != "Not Found":
        memory_size = int(memory_size)
    else:
        memory_size = 0

    if memory_used != "Not Found":
        memory_used = int(memory_used)
    else:
        memory_used = 0

    if hypervisor and hypervisor.get("hypervisor_status") != "disabled":
        hv_info["vcpus_available"] = max(0, vcpus - vcpus_used)
        hv_info["mem_available"] = max(0, memory_size - memory_used)
        hv_info["vcpus_capacity"] = vcpus
        hv_info["mem_capacity"] = memory_size

        hv_info["gpu_capacity"] = int(aggregate_info["metadata"].get("gpunum", "0"))
        hv_info["compute_service_status"] = service_info["status"]

    return hv_info


def get_flavor_requirements(flavor: Dict) -> Dict:
    """
    Helper function to get flavor memory/ram/gpu requirements for a VM of that type to be built on a hv
    :param flavor: flavor to get requirements from
    :return: dictionary of requirements
    """
    try:
        flavor_reqs = {
            "cores_required": int(flavor["vcpus"]),
            "mem_required": int(flavor["ram"]),
        }
    except (ValueError, KeyError) as exp:
        flavor_name = flavor.get("name", "Name Not Found")
        raise RuntimeError(
            f"could not get flavor requirements for flavor {flavor_name}"
        ) from exp

    flavor_reqs.update(
        {
            "gpus_required": int(
                flavor.get("extra_specs", {}).get("accounting:gpu_num", 0)
            ),
        }
    )
    return flavor_reqs


def get_valid_flavors_for_aggregate(flavor_list: List, aggregate: Dict) -> List:
    """
    Helper function that filters a list of flavors
    to find those that can be built on a hv belonging to a given aggregate
    :param flavor_list: a list of flavors to check
    :param aggregate: specifies the aggregate to find compatible flavors for
    :return: a list of valid flavors for hosttype
    """
    valid_flavors = []
    hypervisor_hosttype = aggregate["metadata"].get("hosttype", None)
    hypervisor_storage_type = aggregate["metadata"].get("local-storage-type", None)

    if not hypervisor_hosttype:
        return valid_flavors

    for flavor in flavor_list:
        # validate that flavor can be used on host aggregate
        if (
            "aggregate_instance_extra_specs:hosttype"
            not in flavor["extra_specs"].keys()
        ):
            continue
        if (
            flavor["extra_specs"]["aggregate_instance_extra_specs:hosttype"]
            != hypervisor_hosttype
        ):
            continue

        has_local_storage = (
            "aggregate_instance_extra_specs:local-storage-type"
            in flavor["extra_specs"].keys()
        )

        if (
            has_local_storage
            and flavor["extra_specs"][
                "aggregate_instance_extra_specs:local-storage-type"
            ]
            != hypervisor_storage_type
        ):
            continue

        valid_flavors.append(flavor)
    return valid_flavors


def convert_to_data_string(instance: str, slots_dict: Dict) -> str:
    """
    converts a dictionary of values into a data-string influxdb can read
    :param slots_dict: a dictionary of slots available for each flavor
    :param instance: which cloud the info was scraped from (prod or dev)
    :return: a comma-separated string of key=value taken from input dictionary
    """
    data_string = ""
    for flavor, slot_info in slots_dict.items():
        data_string += (
            f"SlotsAvailable,instance={instance.capitalize()},flavor={flavor}"
            f" SlotsAvailable={slot_info.slots_available}i"
            f",maxSlotsAvailable={slot_info.max_gpu_slots_capacity}i"
            f",usedSlots={slot_info.estimated_gpu_slots_used}i"
            f",enabledSlots={slot_info.max_gpu_slots_capacity_enabled}i\n"
        )
    return data_string


def calculate_slots_on_hv(
    flavor_name: str, flavor_reqs: Dict, hv_info: Dict
) -> SlottifierEntry:
    """
    Helper function that calculates available slots for a flavor on a given hypervisor
    :param flavor_name: name of flavor
    :param flavor_reqs: dictionary of memory, cpu, and gpu requirements of flavor
    :param hv_info: dictionary of memory, cpu, and gpu capacity/availability on hypervisor
        and whether hv compute service is enabled
    :return: A dataclass holding slottifer information to update with
    """
    slots_dataclass = SlottifierEntry()

    slots_available = min(
        hv_info["vcpus_available"] // flavor_reqs["cores_required"],
        hv_info["mem_available"] // flavor_reqs["mem_required"],
    )

    if "g-" in flavor_name:
        # workaround for bugs where gpu number not specified
        if flavor_reqs["gpus_required"] == 0:
            raise RuntimeError(
                f"gpu flavor {flavor_name} does not have 'gpunum' metadata"
            )

        theoretical_gpu_slots_available = min(
            hv_info["gpu_capacity"] // flavor_reqs["gpus_required"],
            hv_info["vcpus_capacity"] // flavor_reqs["cores_required"],
            hv_info["mem_capacity"] // flavor_reqs["mem_required"],
        )

        estimated_slots_used = (
            min(
                hv_info["vcpus_capacity"] // flavor_reqs["cores_required"],
                hv_info["mem_capacity"] // flavor_reqs["mem_required"],
            )
            - slots_available
        )

        # estimated number of GPU slots used - based off of how much cpu/mem is currently being used
        # assumes that all VMs on the HV contains only this flavor -  which may not be true
        # if slots used is greater than gpu slots available we assume all gpus are being used
        slots_dataclass.estimated_gpu_slots_used = min(
            theoretical_gpu_slots_available, estimated_slots_used
        )

        slots_dataclass.max_gpu_slots_capacity = theoretical_gpu_slots_available

        if hv_info["compute_service_status"] == "enabled":
            slots_dataclass.max_gpu_slots_capacity_enabled = (
                theoretical_gpu_slots_available
            )

        slots_available = min(
            slots_available,
            theoretical_gpu_slots_available - slots_dataclass.estimated_gpu_slots_used,
        )

    if hv_info["compute_service_status"] == "enabled":
        slots_dataclass.slots_available = slots_available
    return slots_dataclass


def get_openstack_resources(instance: str) -> Dict:
    """
    This is a helper function that gets information from openstack in one go to calculate flavor slots
    This is quicker than getting resources one at a time
    It queries the Query Library for all hypervisors within the instance.
    :param instance: which cloud to calculate slots for
    :return: a dictionary containing 4 entries, key is an openstack component,
    value is a list of all components of that
    type: compute_services, aggregates, hypervisors and flavors
    """
    conn = openstack.connect(cloud=instance)

    # we get all openstack info first because it is quicker than getting them one at a time
    # dictionaries prevent duplicates

    all_compute_services = {
        service["id"]: service for service in conn.compute.services()
    }
    all_aggregates = {
        aggregate["id"]: aggregate for aggregate in conn.compute.aggregates()
    }

    # Querying the query library
    hv = HypervisorQuery()
    hv.select_all()
    hv.run(instance)
    hv.group_by("id")
    # Flattens the incoming list of dictionaries, into a dictionary of lists
    hv_props = hv.to_props(flatten=True)

    all_hypervisors = {}
    for hypervisor, hv_info in hv_props.items():
        for k, v in hv_info.items():
            hv_info[k] = v[0]
        all_hypervisors[hypervisor] = hv_info

    all_flavors = {
        flavor["id"]: flavor for flavor in conn.compute.flavors(get_extra_specs=True)
    }

    return {
        "compute_services": list(all_compute_services.values()),
        "aggregates": list(all_aggregates.values()),
        "hypervisors": list(all_hypervisors.values()),
        "flavors": list(all_flavors.values()),
    }


def get_all_hv_info_for_aggregate(
    aggregate: Dict, all_compute_services: List, all_hypervisors: List
) -> List:
    """
    helper function to get all useful info from hypervisors belonging to a given aggregate
    :param aggregate: aggregate that we want to get hvs for
    :param all_compute_services: all compute services to validate hvs against
        - ensure they have a nova_compute service attached
    :param all_hypervisors: all hypervisors to get hv info from
    :return: list of dictionaries of hypervisor information for calculating slots
    """

    valid_hvs = []
    for host in aggregate["hosts"]:
        host_compute_service = None
        for compute_service in all_compute_services:
            if compute_service["host"] == host:
                host_compute_service = compute_service

        if not host_compute_service:
            continue

        hv_obj = None
        for hypervisor in all_hypervisors:
            if host_compute_service["host"] == hypervisor["hypervisor_name"]:
                hv_obj = hypervisor

        if not hv_obj:
            continue

        valid_hvs.append(get_hv_info(hv_obj, aggregate, host_compute_service))
    return valid_hvs


def update_slots(flavors: List, host_info_list: List, slots_dict: Dict) -> Dict:
    """
    update total slots by calculating slots available for a set of flavors on a set of hosts
    :param flavors: a list of flavors
    :param host_info_list: a list of dictionaries holding info about a hypervisor capacity/availability
    :param slots_dict: dictionary of slot info to update
    :return:
    """

    for flavor in flavors:
        flavor_reqs = get_flavor_requirements(flavor)
        for hypervisor in host_info_list:
            slots_dict[flavor["name"]] += calculate_slots_on_hv(
                flavor["name"], flavor_reqs, hypervisor
            )
    return slots_dict


def get_slottifier_details(instance: str) -> str:
    """
    This function gets calculates slots available for each flavor in openstack and outputs results in
    data string format which can be posted to InfluxDB
    :param instance: which cloud to calculate slots for
    :return: A data string of scraped info
    """
    all_openstack_info = get_openstack_resources(instance)

    slots_dict = {
        flavor["name"]: SlottifierEntry() for flavor in all_openstack_info["flavors"]
    }
    for aggregate in all_openstack_info["aggregates"]:
        valid_flavors = get_valid_flavors_for_aggregate(
            all_openstack_info["flavors"], aggregate
        )

        aggregate_host_info = get_all_hv_info_for_aggregate(
            aggregate,
            all_openstack_info["compute_services"],
            all_openstack_info["hypervisors"],
        )

        slots_dict = update_slots(valid_flavors, aggregate_host_info, slots_dict)

    return convert_to_data_string(instance, slots_dict)


def main(user_args: List):
    """
    send slottifier info to influx
    :param user_args: args passed into script by user
    """
    influxdb_args = parse_args(user_args, description="Get All Service Statuses")
    run_scrape(influxdb_args, get_slottifier_details)


if __name__ == "__main__":
    main(sys.argv[1:])
