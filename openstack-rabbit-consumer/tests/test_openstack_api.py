# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Tests that the Openstack API functions are invoked
as expected with the correct params
"""
from unittest.mock import NonCallableMock, patch

# noinspection PyUnresolvedReferences
from rabbit_consumer.openstack_api import (
    update_metadata,
    OpenstackConnection,
    check_machine_exists,
    get_server_details,
    get_server_networks,
    get_image,
)


@patch("rabbit_consumer.openstack_api.ConsumerConfig")
@patch("rabbit_consumer.openstack_api.openstack.connect")
def test_openstack_connection(mock_connect, mock_config):
    """
    Test that the OpenstackConnection context manager calls the correct functions
    """
    with OpenstackConnection() as conn:
        mock_connect.assert_called_once_with(
            auth_url=mock_config.return_value.openstack_auth_url,
            username=mock_config.return_value.openstack_username,
            password=mock_config.return_value.openstack_password,
            project_name="admin",
            user_domain_name="Default",
            project_domain_name="default",
        )

        # Pylint is unable to see that openstack.connect returns a mock
        # pylint: disable=no-member
        assert conn == mock_connect.return_value
        # pylint: disable=no-member
        assert conn.close.call_count == 0

    # Check close is called when the context manager exits
    # pylint: disable=no-member
    assert conn.close.call_count == 1


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_check_machine_exists_existing_machine(conn, vm_data):
    """
    Test that the function returns True when the machine exists
    """
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.return_value = NonCallableMock()
    found = check_machine_exists(vm_data)

    conn.assert_called_once_with()
    context.compute.find_server.assert_called_with(vm_data.virtual_machine_id)
    assert isinstance(found, bool) and found


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_check_machine_exists_deleted_machine(conn, vm_data):
    """
    Test that the function returns False when the machine does not exist
    """
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.return_value = None
    found = check_machine_exists(vm_data)

    conn.assert_called_once_with()
    context = conn.return_value.__enter__.return_value
    context.compute.find_server.assert_called_with(vm_data.virtual_machine_id)
    assert isinstance(found, bool) and not found


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
@patch("rabbit_consumer.openstack_api.get_server_details")
def test_update_metadata(server_details, conn, vm_data):
    """
    Test that the function calls the correct functions to update the metadata on a VM
    """
    server_details.return_value = NonCallableMock()
    update_metadata(vm_data, {"key": "value"})

    server_details.assert_called_once_with(vm_data)

    conn.assert_called_once_with()
    context = conn.return_value.__enter__.return_value
    context.compute.set_server_metadata.assert_called_once_with(
        server_details.return_value, **{"key": "value"}
    )


@patch("rabbit_consumer.openstack_api.OpenstackConnection")
def test_get_server_details(conn, vm_data):
    """
    Test that the function calls the correct functions to get the details of a VM
    """
    context = conn.return_value.__enter__.return_value
    context.compute.servers.return_value = [NonCallableMock()]

    result = get_server_details(vm_data)

    context.compute.servers.assert_called_once_with(
        uuid=vm_data.virtual_machine_id, all_projects=True
    )

    assert result == context.compute.servers.return_value[0]


@patch("rabbit_consumer.openstack_api.get_server_details")
@patch("rabbit_consumer.openstack_api.OpenstackAddress")
def test_get_server_networks_internal(address, server_details, vm_data):
    """
    Test that the function calls the correct functions to get the networks of a VM
    """
    server_details.return_value.addresses = {"Internal": []}

    get_server_networks(vm_data)
    address.get_internal_networks.assert_called_once_with(
        server_details.return_value.addresses
    )


@patch("rabbit_consumer.openstack_api.get_server_details")
@patch("rabbit_consumer.openstack_api.OpenstackAddress")
def test_get_server_networks_services(address, server_details, vm_data):
    """
    Test that the function calls the correct functions to get the networks of a VM
    """
    server_details.return_value.addresses = {"Services": []}

    get_server_networks(vm_data)
    address.get_services_networks.assert_called_once_with(
        server_details.return_value.addresses
    )


@patch("rabbit_consumer.openstack_api.get_server_details")
def test_get_server_networks_no_network(server_details, vm_data):
    """
    Tests that an empty list is returned when there are no networks
    """
    server_details.return_value = NonCallableMock()
    server_details.return_value.addresses = {}

    result = get_server_networks(vm_data)
    assert not result


@patch("rabbit_consumer.openstack_api.get_server_details")
def test_get_image_no_image_id(server_details, vm_data):
    """
    Tests that get image handles an empty image UUID
    usually when a volume was used instead of an image
    """
    server_details.return_value = NonCallableMock()
    server_details.return_value.image.id = None

    result = get_image(vm_data)
    assert not result
