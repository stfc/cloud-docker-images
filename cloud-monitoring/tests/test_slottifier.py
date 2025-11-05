from unittest.mock import NonCallableMock, MagicMock, patch, call
from cloudMonitoring.slottifier import (
    get_hv_info,
    get_flavor_requirements,
    get_valid_flavors_for_aggregate,
    convert_to_data_string,
    calculate_slots_on_hv,
    get_openstack_resources,
    get_all_hv_info_for_aggregate,
    update_slots,
    get_slottifier_details,
    main,
)
import pytest

from cloudMonitoring.structs.slottifier_entry import SlottifierEntry


@pytest.fixture(name="mock_hypervisors")
def mock_hypervisors_fixture():
    """fixture for setting up various mock hvs"""
    return {
        "hv1": {
            "hypervisor_name": "hv1",
            "hypervisor_status": "enabled",
            "hypervisor_vcpus": 8,
            "hypervisor_vcpus_used": 2,
            "hypervisor_memory_size": 8192,
            "hypervisor_memory_used": 2048,
        },
        "hv2": {
            "hypervisor_name": "hv2",
            "hypervisor_status": "enabled",
            "hypervisor_vcpus": 4,
            "hypervisor_vcpus_used": 6,
            "hypervisor_memory_size": 2048,
            "hypervisor_memory_used": 4096,
        },
        "hv3": {
            "hypervisor_name": "hv3",
            "hypervisor_status": "disabled",
        },
        "hv4": {
            "hypervisor_name": "hv4",
            "hypervisor_status": "enabled",
            "hypervisor_vcpus": "Not Found",
            "hypervisor_vcpus_used": "Not Found",
            "hypervisor_memory_size": "Not Found",
            "hypervisor_memory_used": "Not Found",
        },
    }


@pytest.fixture(name="mock_compute_services")
def mock_service_fixture():
    """
    Returns a mock set of services to use as test data
    """
    return {
        "svc1": {"host": "hv1", "name": "svc1"},
        "svc2": {"host": "hv2", "name": "svc2"},
        "svc3": {"host": "hv4", "name": "svc3"},
    }


@pytest.fixture(name="mock_aggregate")
def mock_aggregate_fixture():
    """fixture for setting up a mock aggregate"""

    def _mock_aggregate(hosttype=None, gpu_num=None, storagetype=None):
        """
        helper function for setting up mock aggregate
        :param hosttype: optional hosttype to set
        :param gpu_num: optional gpu_num to set
        :param storagetype: optional storagetype to set
        """
        aggregate = {"metadata": {}}
        if hosttype:
            aggregate["metadata"]["hosttype"] = hosttype
        if gpu_num:
            aggregate["metadata"]["gpunum"] = gpu_num
        if storagetype:
            aggregate["metadata"]["local-storage-type"] = storagetype
        return aggregate

    return _mock_aggregate


@pytest.fixture(name="mock_flavors_list")
def mock_flavors_fixture():
    """fixture for setting up various mock flavors"""
    return [
        {"id": 1, "extra_specs": {"aggregate_instance_extra_specs:hosttype": "A"}},
        {"id": 2, "extra_specs": {"aggregate_instance_extra_specs:hosttype": "B"}},
        {"id": 3, "extra_specs": {}},
        {"id": 4, "extra_specs": {"aggregate_instance_extra_specs:hosttype": "A"}},
        {
            "id": 5,
            "extra_specs": {
                "aggregate_instance_extra_specs:hosttype": "C",
                "aggregate_instance_extra_specs:local-storage-type": "1",
            },
        },
        {
            "id": 6,
            "extra_specs": {
                "aggregate_instance_extra_specs:hosttype": "C",
                "aggregate_instance_extra_specs:local-storage-type": "2",
            },
        },
    ]


def test_get_hv_info_exists_and_enabled(mock_hypervisors, mock_aggregate):
    """tests get_hv_info when hv exists and enabled - should parse results properly"""

    assert get_hv_info(
        mock_hypervisors["hv1"], mock_aggregate(gpu_num="1"), {"status": "enabled"}
    ) == {
        "vcpus_available": 6,
        "mem_available": 6144,
        "gpu_capacity": 1,
        "vcpus_capacity": 8,
        "mem_capacity": 8192,
        "compute_service_status": "enabled",
    }


def test_get_hv_info_negative_results_floored(mock_hypervisors, mock_aggregate):
    """
    tests get_hv_info when results for available mem/cores are negative
        - should set it to 0 instead
    """

    assert get_hv_info(
        mock_hypervisors["hv2"], mock_aggregate(), {"status": "enabled"}
    ) == {
        "vcpus_available": 0,
        "mem_available": 0,
        "gpu_capacity": 0,
        "vcpus_capacity": 4,
        "mem_capacity": 2048,
        "compute_service_status": "enabled",
    }


def test_get_hv_info_exists_but_disabled(mock_hypervisors, mock_aggregate):
    """
    tests get_hv_info when hv is disabled - should return default results
    """
    assert get_hv_info(
        mock_hypervisors["hv3"], mock_aggregate(), {"status": "disabled"}
    ) == {
        "vcpus_available": 0,
        "mem_available": 0,
        "gpu_capacity": 0,
        "vcpus_capacity": 0,
        "mem_capacity": 0,
        "compute_service_status": "disabled",
    }


def test_get_hv_info_but_values_are_not_found(mock_hypervisors, mock_aggregate):
    """
    tests strings that contain values of "Not_Found" - should return all "Not Found" values as 0
    """
    assert get_hv_info(
        mock_hypervisors["hv4"], mock_aggregate(), {"status": "enabled"}
    ) == {
        "vcpus_available": 0,
        "mem_available": 0,
        "gpu_capacity": 0,
        "vcpus_capacity": 0,
        "mem_capacity": 0,
        "compute_service_status": "enabled",
    }


def test_get_flavor_requirements_with_valid_flavor():
    """
    tests get_flavor_requirements with valid flavor
    """
    mock_flavor = {
        "extra_specs": {"accounting:gpu_num": "2"},
        "vcpus": "4",
        "ram": "8192",
    }
    assert get_flavor_requirements(mock_flavor) == {
        "gpus_required": 2,
        "cores_required": 4,
        "mem_required": 8192,
    }


def test_get_flavor_requirements_with_missing_values():
    """
    tests get_flavor_requirements with all missing values
        - should return 0s for requirements
    """
    with pytest.raises(RuntimeError):
        get_flavor_requirements({})


def test_get_flavor_requirements_with_partial_values():
    """
    tests get_flavor_requirements with missing gpu_num attr
    should default it to 0
    """
    req_dict = {"ram": "8192", "vcpus": 8}
    assert get_flavor_requirements(req_dict) == {
        "gpus_required": 0,
        "cores_required": 8,
        "mem_required": 8192,
    }


def test_get_valid_flavors_with_matching_type(mock_flavors_list, mock_aggregate):
    """
    test get_valid_flavors_for_aggregate should find all flavors with matching
    aggregate hosttype
    """
    assert get_valid_flavors_for_aggregate(mock_flavors_list, mock_aggregate("A")) == [
        {"id": 1, "extra_specs": {"aggregate_instance_extra_specs:hosttype": "A"}},
        {"id": 4, "extra_specs": {"aggregate_instance_extra_specs:hosttype": "A"}},
    ]


def test_get_valid_flavors_with_empty_flavors_list(mock_aggregate):
    """
    test get_valid_flavors_for_aggregate should return empty list if no flavors given
    """
    assert not get_valid_flavors_for_aggregate([], mock_aggregate("A"))


def test_get_valid_flavors_with_non_matching_hosttype(
    mock_flavors_list, mock_aggregate
):
    """
    test get_valid_flavors_for_aggregate should return empty list if no flavors found with
    matching aggregate hosttype
    """
    assert not get_valid_flavors_for_aggregate(mock_flavors_list, mock_aggregate("D"))


def test_get_valid_flavors_with_storagetype(mock_flavors_list, mock_aggregate):
    """
    test get_valid_flavors_for_aggregate should return list of hvs with matching hosttype and storagetype
    """
    assert get_valid_flavors_for_aggregate(
        mock_flavors_list, mock_aggregate(hosttype="C", storagetype="1")
    ) == [
        {
            "id": 5,
            "extra_specs": {
                "aggregate_instance_extra_specs:hosttype": "C",
                "aggregate_instance_extra_specs:local-storage-type": "1",
            },
        },
    ]


def test_convert_to_data_string_no_items():
    """
    Tests convert_to_data_string returns empty string when given empty dict as slots_dict
    """
    assert not convert_to_data_string(NonCallableMock(), {})


def test_convert_to_data_string_one_item():
    """
    Tests convert_to_data_string works with single entry in dict for slots_dict
    """
    mock_instance = "prod"

    mock_slot_info_dataclass = MagicMock()
    mock_slot_info_dataclass.slots_available = "1"
    mock_slot_info_dataclass.max_gpu_slots_capacity = "2"
    mock_slot_info_dataclass.estimated_gpu_slots_used = "3"
    mock_slot_info_dataclass.max_gpu_slots_capacity_enabled = "4"

    mock_slots_dict = {"flavor1": mock_slot_info_dataclass}

    res = convert_to_data_string(mock_instance, mock_slots_dict)
    assert res == (
        "SlotsAvailable,instance=Prod,flavor=flavor1 "
        "SlotsAvailable=1i,maxSlotsAvailable=2i,usedSlots=3i,enabledSlots=4i\n"
    )


def test_convert_to_data_string_multi_item():
    """
    Tests convert_to_data_string works with multiple entries in dict for slots_dict
    """
    mock_instance = "prod"
    mock_slot_info_dataclass = MagicMock()
    mock_slot_info_dataclass.slots_available = "1"
    mock_slot_info_dataclass.max_gpu_slots_capacity = "2"
    mock_slot_info_dataclass.estimated_gpu_slots_used = "3"
    mock_slot_info_dataclass.max_gpu_slots_capacity_enabled = "4"

    mock_slots_dict = {
        "flavor1": mock_slot_info_dataclass,
        "flavor2": mock_slot_info_dataclass,
    }

    res = convert_to_data_string(mock_instance, mock_slots_dict)
    assert res == (
        "SlotsAvailable,instance=Prod,flavor=flavor1 "
        "SlotsAvailable=1i,maxSlotsAvailable=2i,usedSlots=3i,enabledSlots=4i\n"
        "SlotsAvailable,instance=Prod,flavor=flavor2 "
        "SlotsAvailable=1i,maxSlotsAvailable=2i,usedSlots=3i,enabledSlots=4i\n"
    )


def test_calculate_slots_on_hv_non_gpu_disabled():
    """
    tests calculate_slots_on_hv calculates slots properly for non-gpu flavor
        - should return 0s since hv is disabled
    """
    res = calculate_slots_on_hv(
        "flavor1",
        {"cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "disabled",
            # can fit 10 slots, but should be 0 since compute service disabled
            "vcpus_available": 100,
            "mem_available": 100,
        },
    )
    assert res.slots_available == 0
    assert res.max_gpu_slots_capacity == 0
    assert res.estimated_gpu_slots_used == 0
    assert res.max_gpu_slots_capacity_enabled == 0


def test_calculate_slots_on_hv_gpu_no_gpunum():
    """
    tests calculate_slots_on_hv when provided a gpu flavor but gpus_required is set to 0
    should raise error
    """
    with pytest.raises(RuntimeError):
        calculate_slots_on_hv(
            # g- specifies gpu flavor
            "g-flavor1",
            {"gpus_required": 0, "cores_required": 10, "mem_required": 10},
            {
                "compute_service_status": "disabled",
                # can fit 10 slots, but should be 0 since compute service disabled
                "vcpus_available": 100,
                "mem_available": 100,
            },
        )


def test_calculate_slots_on_hv_gpu_disabled():
    """
    tests calculate_slots_on_hv calculates slots properly for gpu flavor
        - should return 0s since hv is disabled, but keep track of max gpu slots capacity
    """

    res = calculate_slots_on_hv(
        # g- specifies gpu flavor
        "g-flavor1",
        {"gpus_required": 1, "cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "disabled",
            # can fit 10 slots, but should be 0 since compute service disabled
            "vcpus_available": 100,
            "mem_available": 100,
            "vcpus_capacity": 100,
            "mem_capacity": 100,
            "gpu_capacity": 10,
        },
    )
    assert res.slots_available == 0
    # still want capacity to be updated
    assert res.max_gpu_slots_capacity == 10
    assert res.estimated_gpu_slots_used == 0
    assert res.max_gpu_slots_capacity_enabled == 0


def test_calculate_slots_on_hv_mem_available_max():
    """
    tests calculate_slots_on_hv calculates slots properly for non-gpu flavor
    - where memory available is limiting factor
    """

    res = calculate_slots_on_hv(
        "flavor1",
        {"cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "enabled",
            "vcpus_available": 100,
            # can fit only one slot
            "mem_available": 10,
        },
    )
    assert res.slots_available == 1
    assert res.max_gpu_slots_capacity == 0
    assert res.estimated_gpu_slots_used == 0
    assert res.max_gpu_slots_capacity_enabled == 0


def test_calculate_slots_on_hv_cores_available_max():
    """
    tests calculate_slots_on_hv calculates slots properly for non-gpu flavor
    - where cores available is limiting factor
    """
    res = calculate_slots_on_hv(
        "flavor1",
        {"cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "enabled",
            # can fit 10 cpu slots
            "vcpus_available": 100,
            "mem_available": 1000,
        },
    )
    assert res.slots_available == 10
    assert res.max_gpu_slots_capacity == 0
    assert res.estimated_gpu_slots_used == 0
    assert res.max_gpu_slots_capacity_enabled == 0


def test_calculate_slots_on_hv_gpu_available_max():
    """
    tests calculate_slots_on_hv calculates slots properly for gpu flavor
    - where gpus available is limiting factor
    """
    res = calculate_slots_on_hv(
        # specifies a gpu flavor
        "g-flavor1",
        {"gpus_required": 1, "cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "enabled",
            # should find only 5 slots available since gpus are the limiting factor
            "gpu_capacity": 5,
            "vcpus_available": 100,
            "mem_available": 100,
            "vcpus_capacity": 100,
            "mem_capacity": 100,
        },
    )
    assert res.slots_available == 5
    assert res.max_gpu_slots_capacity == 5
    assert res.estimated_gpu_slots_used == 0
    assert res.max_gpu_slots_capacity_enabled == 5


def test_calculate_slots_on_hv_gpu_max_slots_calculated_properly():
    """
    tests calculate_slots_on_hv calculates max slots properly for gpu flavor
    """
    res = calculate_slots_on_hv(
        # specifies a gpu flavor
        "g-flavor1",
        {"gpus_required": 2, "cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "enabled",
            # should find 3 slots since we require 2 gpus for each slot
            "gpu_capacity": 6,
            "vcpus_available": 100,
            "mem_available": 100,
            "vcpus_capacity": 100,
            "mem_capacity": 100,
        },
    )
    assert res.slots_available == 3
    assert res.max_gpu_slots_capacity == 3
    assert res.estimated_gpu_slots_used == 0
    assert res.max_gpu_slots_capacity_enabled == 3


def test_calculate_slots_on_hv_calculates_used_gpu_capacity():
    """
    tests calculate_slots_on_hv calculates slots properly for gpu flavor
    - should calculate estimated used gpus slots properly
    """
    res = calculate_slots_on_hv(
        # specifies a gpu flavor
        "g-flavor1",
        {"gpus_required": 1, "cores_required": 10, "mem_required": 10},
        {
            "compute_service_status": "enabled",
            # should find only 5 slots available since gpus are the limiting factor
            "gpu_capacity": 5,
            "vcpus_available": 10,
            "mem_available": 10,
            # there's 4 flavor slots that could have already been used
            "vcpus_capacity": 50,
            "mem_capacity": 50,
        },
    )
    assert res.slots_available == 1
    assert res.max_gpu_slots_capacity == 5
    assert res.estimated_gpu_slots_used == 4
    assert res.max_gpu_slots_capacity_enabled == 5


@patch("cloudMonitoring.slottifier.openstack")
@patch("cloudMonitoring.slottifier.HypervisorQuery")
def test_get_openstack_resources(
    mock_hypervisor_query, mock_openstack
):  # do I use self?
    """
    tests get_openstack_resources gets all required resources via openstacksdk
    and the query library and outputs them properly
    """
    mock_conn = mock_openstack.connect.return_value

    # Run the mock queries
    mock_hv = mock_hypervisor_query.return_value

    # Create a mock hv_props dictionary.
    mock_hv.to_props.return_value = {
        "hypervisor1": {"id": [1], "name": ["hv1"]},
        "hypervisor2": {"id": [2], "name": ["hv2"]},
    }

    mock_conn.compute.aggregates.return_value = [{"name": "ag1", "id": 2}]
    mock_conn.compute.services.return_value = [{"name": "svc1", "id": 3}]
    mock_conn.compute.flavors.return_value = [{"name": "flv1", "id": 4}]

    mock_instance = NonCallableMock()
    res = get_openstack_resources(mock_instance)

    mock_hv.select_all.assert_called_once()
    mock_hv.run.assert_called_once_with(mock_instance)
    mock_hv.group_by.assert_called_once_with("id")

    mock_openstack.connect.assert_called_once_with(cloud=mock_instance)
    mock_conn.compute.services.assert_called_once()
    mock_conn.compute.aggregates.assert_called_once()
    mock_conn.compute.flavors.assert_called_once_with(get_extra_specs=True)

    assert res == {
        "compute_services": [{"name": "svc1", "id": 3}],
        "aggregates": [{"name": "ag1", "id": 2}],
        "hypervisors": [{"name": "hv1", "id": 1}, {"name": "hv2", "id": 2}],
        "flavors": [{"name": "flv1", "id": 4}],
    }


@patch("cloudMonitoring.slottifier.get_hv_info")
def test_get_all_hv_info_for_aggregate_with_valid_data(
    mock_get_hv_info, mock_hypervisors, mock_compute_services
):
    """
    Tests get_all_hv_info_for_aggregate with valid data.
    should call get_hv_info with correct hv and service object that match aggregate and
    add results to list
    """
    mock_aggregate = {"hosts": ["hv1", "hv2"]}
    res = get_all_hv_info_for_aggregate(
        mock_aggregate, mock_compute_services.values(), mock_hypervisors.values()
    )
    mock_get_hv_info.assert_has_calls(
        [
            # svc1 holds host: hv1
            call(
                mock_hypervisors["hv1"], mock_aggregate, mock_compute_services["svc1"]
            ),
            # svc2 holds host: hv2
            call(
                mock_hypervisors["hv2"], mock_aggregate, mock_compute_services["svc2"]
            ),
        ]
    )
    assert res == [mock_get_hv_info.return_value, mock_get_hv_info.return_value]


def test_get_all_hv_info_for_aggregate_with_invalid_data(
    mock_hypervisors, mock_compute_services
):
    """
    Tests get_all_hv_info_for_aggregate with invalid data.
    should not add hv with invalid data to the resulting list
    """
    mock_aggregate = {
        "hosts": [
            # hvFoo has service but not found in list of hvs
            "hvFoo",
            # hvBar has no service and not in list of hvs
            "hvBar",
        ]
    }
    assert not (
        get_all_hv_info_for_aggregate(
            mock_aggregate, mock_compute_services.values(), mock_hypervisors.values()
        )
    )


def test_get_all_hv_info_for_aggregate_with_empty_aggregate(
    mock_hypervisors, mock_compute_services
):
    """
    Tests get_all_hv_info_for_aggregate with aggregate with no hosts.
    should do nothing and return empty list
    """
    mock_aggregate = {"hosts": []}
    assert not (
        get_all_hv_info_for_aggregate(
            mock_aggregate, mock_hypervisors.values(), mock_compute_services.values()
        )
    )


@patch("cloudMonitoring.slottifier.get_flavor_requirements")
@patch("cloudMonitoring.slottifier.calculate_slots_on_hv")
def test_update_slots_one_flavor_one_hv(
    mock_calculate_slots_on_hv, mock_get_flavor_requirements
):
    """
    Tests update_slots with one flavor and one hv.
    should call calculate_slots_on_hv once with the given flavor and hv
    """
    mock_flavor = {"name": "flv1"}
    mock_host = NonCallableMock()

    slots_dict = {"flv1": 1}
    mock_calculate_slots_on_hv.return_value = 1
    res = update_slots([mock_flavor], [mock_host], slots_dict=slots_dict)
    mock_get_flavor_requirements.assert_called_once_with(mock_flavor)
    mock_calculate_slots_on_hv.assert_called_once_with(
        "flv1", mock_get_flavor_requirements.return_value, mock_host
    )
    assert res == {"flv1": 2}


@patch("cloudMonitoring.slottifier.get_flavor_requirements")
@patch("cloudMonitoring.slottifier.calculate_slots_on_hv")
def test_update_slots_one_flavor_multi_hv(
    mock_calculate_slots_on_hv, mock_get_flavor_requirements
):
    """
    Tests update_slots with one flavor and multiple hvs.
    should call calculate_slots_on_hv on each hv with the same flavor
    """
    mock_flavor = {"name": "flv1"}
    mock_host_1 = NonCallableMock()
    mock_host_2 = NonCallableMock()
    slots_dict = {"flv1": 1}
    mock_calculate_slots_on_hv.side_effect = [1, 2]
    res = update_slots([mock_flavor], [mock_host_1, mock_host_2], slots_dict=slots_dict)
    mock_get_flavor_requirements.assert_called_once_with(mock_flavor)
    mock_calculate_slots_on_hv.assert_has_calls(
        [
            call("flv1", mock_get_flavor_requirements.return_value, mock_host_1),
            call("flv1", mock_get_flavor_requirements.return_value, mock_host_2),
        ]
    )
    assert res == {"flv1": 4}


@patch("cloudMonitoring.slottifier.get_flavor_requirements")
@patch("cloudMonitoring.slottifier.calculate_slots_on_hv")
def test_update_slots_multi_flavor_multi_hv(
    mock_calculate_slots_on_hv, mock_get_flavor_requirements
):
    """
    Tests update_slots with multiple flavors and multiple hvs.
    should call calculate_slots_on_hv with each unique hv-flavor pairings
    """
    mock_flavor_1 = {"name": "flv1"}
    mock_flavor_2 = {"name": "flv2"}
    mock_host_1 = NonCallableMock()
    mock_host_2 = NonCallableMock()
    slots_dict = {"flv1": 1, "flv2": 0}
    mock_calculate_slots_on_hv.side_effect = [1, 2, 0, 0]
    res = update_slots(
        [mock_flavor_1, mock_flavor_2],
        [mock_host_1, mock_host_2],
        slots_dict=slots_dict,
    )
    mock_get_flavor_requirements.assert_has_calls(
        [call(mock_flavor_1), call(mock_flavor_2)]
    )
    mock_calculate_slots_on_hv.assert_has_calls(
        [
            call("flv1", mock_get_flavor_requirements.return_value, mock_host_1),
            call("flv1", mock_get_flavor_requirements.return_value, mock_host_2),
            call("flv2", mock_get_flavor_requirements.return_value, mock_host_1),
            call("flv2", mock_get_flavor_requirements.return_value, mock_host_2),
        ]
    )
    assert res == {"flv1": 4, "flv2": 0}


@patch("cloudMonitoring.slottifier.get_openstack_resources")
@patch("cloudMonitoring.slottifier.get_valid_flavors_for_aggregate")
@patch("cloudMonitoring.slottifier.get_all_hv_info_for_aggregate")
@patch("cloudMonitoring.slottifier.update_slots")
@patch("cloudMonitoring.slottifier.convert_to_data_string")
def test_get_slottifier_details_one_aggregate(
    mock_convert_to_data_string,
    mock_update_slots,
    mock_get_all_hv_info_for_aggregate,
    mock_get_valid_flavors_for_aggregate,
    mock_get_openstack_resources,
):
    """
    Tests get_slottifier_details with one aggregate.
    """
    mock_instance = NonCallableMock()
    mock_flavors = [{"name": "flv1"}, {"name": "flv2"}]
    mock_compute_services = NonCallableMock()
    mock_hypervisors = NonCallableMock()

    mock_get_openstack_resources.return_value = {
        "aggregates": ["ag1"],
        "flavors": mock_flavors,
        "compute_services": mock_compute_services,
        "hypervisors": mock_hypervisors,
    }
    res = get_slottifier_details(mock_instance)
    mock_get_openstack_resources.assert_called_once_with(mock_instance)
    mock_get_valid_flavors_for_aggregate.assert_called_once_with(mock_flavors, "ag1")
    mock_get_all_hv_info_for_aggregate.assert_called_once_with(
        "ag1", mock_compute_services, mock_hypervisors
    )

    mock_update_slots.assert_called_once_with(
        mock_get_valid_flavors_for_aggregate.return_value,
        mock_get_all_hv_info_for_aggregate.return_value,
        {"flv1": SlottifierEntry(), "flv2": SlottifierEntry()},
    )

    mock_convert_to_data_string.assert_called_once_with(
        mock_instance, mock_update_slots.return_value
    )
    assert res == mock_convert_to_data_string.return_value


@patch("cloudMonitoring.slottifier.run_scrape")
@patch("cloudMonitoring.slottifier.parse_args")
def test_main(mock_parse_args, mock_run_scrape):
    """
    tests main function calls run_scrape utility function properly
    """
    mock_user_args = NonCallableMock()
    main(mock_user_args)
    mock_run_scrape.assert_called_once_with(
        mock_parse_args.return_value, get_slottifier_details
    )
    mock_parse_args.assert_called_once_with(
        mock_user_args, description="Get All Service Statuses"
    )
