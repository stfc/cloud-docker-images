# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Tests the dataclass representing OpenStack network addresses
"""
import copy
from unittest.mock import patch

import pytest

from rabbit_consumer.openstack_address import OpenstackAddress


@pytest.fixture(name="example_dict_internal")
def fixture_example_dict_internal():
    """
    Creates a dictionary with mock data representing the network addresses of an internal VM
    """
    # Adapted from real response from OpenStack API
    return {
        "Internal": [
            {
                "OS-EXT-IPS-MAC:mac_addr": "fa:ca:aa:aa:aa:aa",
                "version": 4,
                "addr": "127.0.0.63",
                "OS-EXT-IPS:type": "fixed",
            }
        ]
    }


@pytest.fixture(name="example_dict_two_entries_internal")
def fixture_example_dict_two_entries_internal(example_dict_internal):
    """
    Creates a dictionary with mock data representing the network addresses of an internal VM with two entries
    """
    second = copy.deepcopy(example_dict_internal["Internal"][0])
    second["addr"] = "127.0.0.64"
    example_dict_internal["Internal"].append(second)
    return example_dict_internal


@patch("rabbit_consumer.openstack_address.socket.gethostbyaddr")
def test_openstack_address_single_case_internal(mock_socket, example_dict_internal):
    """
    Tests the OpenstackAddress class with a single internal network address
    """
    result = OpenstackAddress.get_internal_networks(example_dict_internal)
    assert len(result) == 1
    assert result[0].version == 4
    assert result[0].addr == "127.0.0.63"
    assert result[0].mac_addr == "fa:ca:aa:aa:aa:aa"
    mock_socket.assert_called_once()


@patch("rabbit_consumer.openstack_address.socket.gethostbyaddr")
def test_openstack_address_multiple_networks_internal(
    mock_socket, example_dict_two_entries_internal
):
    """
    Tests the OpenstackAddress class with multiple internal network addresses
    """
    result = OpenstackAddress.get_internal_networks(example_dict_two_entries_internal)
    assert len(result) == 2
    assert result[0].version == 4
    assert result[0].addr == "127.0.0.63"
    assert result[1].addr == "127.0.0.64"
    mock_socket.assert_called()


@patch("rabbit_consumer.openstack_address.socket.gethostbyaddr")
def test_openstack_address_populate_internal(
    mock_socket, example_dict_two_entries_internal
):
    """
    Tests the OpenstackAddress class with multiple internal network addresses
    """
    mock_socket.side_effect = [("hostname", None, None), ("hostname2", None, None)]
    result = OpenstackAddress.get_internal_networks(example_dict_two_entries_internal)

    assert result[0].hostname == "hostname"
    assert result[1].hostname == "hostname2"

    assert mock_socket.call_count == 2
    assert mock_socket.call_args_list[0][0][0] == "127.0.0.63"
    assert mock_socket.call_args_list[1][0][0] == "127.0.0.64"


@pytest.fixture(name="example_dict_services")
def fixture_example_dict_services():
    """
    Creates a dictionary with mock data representing the services network addresses of a VM
    """
    # Adapted from real response from OpenStack API
    return {
        "Services": [
            {
                "OS-EXT-IPS-MAC:mac_addr": "fa:ca:aa:aa:aa:aa",
                "version": 4,
                "addr": "127.0.0.63",
                "OS-EXT-IPS:type": "fixed",
            }
        ]
    }


@pytest.fixture(name="example_dict_two_entries_services")
def fixture_example_dict_two_entries_services(example_dict_services):
    """
    Creates a dictionary with mock data representing the services network addresses of a VM with two entries
    """
    second = copy.deepcopy(example_dict_services["Services"][0])
    second["addr"] = "127.0.0.64"
    example_dict_services["Services"].append(second)
    return example_dict_services


@patch("rabbit_consumer.openstack_address.socket.gethostbyaddr")
def test_openstack_address_single_case_services(mock_socket, example_dict_services):
    """
    Tests the OpenstackAddress class with a single services network address
    """
    result = OpenstackAddress.get_services_networks(example_dict_services)
    assert len(result) == 1
    assert result[0].version == 4
    assert result[0].addr == "127.0.0.63"
    assert result[0].mac_addr == "fa:ca:aa:aa:aa:aa"
    mock_socket.assert_called_once()


@patch("rabbit_consumer.openstack_address.socket.gethostbyaddr")
def test_openstack_address_multiple_networks_services(
    mock_socket, example_dict_two_entries_services
):
    """
    Tests the OpenstackAddress class with multiple services network addresses
    """
    result = OpenstackAddress.get_services_networks(example_dict_two_entries_services)
    assert len(result) == 2
    assert result[0].version == 4
    assert result[0].addr == "127.0.0.63"
    assert result[1].addr == "127.0.0.64"
    mock_socket.assert_called()


@patch("rabbit_consumer.openstack_address.socket.gethostbyaddr")
def test_openstack_address_populate_services(
    mock_socket, example_dict_two_entries_services
):
    """
    Tests the OpenstackAddress class with services multiple network addresses
    """
    mock_socket.side_effect = [("hostname", None, None), ("hostname2", None, None)]
    result = OpenstackAddress.get_services_networks(example_dict_two_entries_services)

    assert result[0].hostname == "hostname"
    assert result[1].hostname == "hostname2"

    assert mock_socket.call_count == 2
    assert mock_socket.call_args_list[0][0][0] == "127.0.0.63"
    assert mock_socket.call_args_list[1][0][0] == "127.0.0.64"
