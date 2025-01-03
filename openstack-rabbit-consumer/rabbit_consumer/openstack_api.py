# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
This file defines methods for connecting and interacting with the 
OpenStack API
"""
import logging
from typing import List, Optional

import openstack
from openstack.compute.v2.image import Image
from openstack.compute.v2.server import Server

from rabbit_consumer.consumer_config import ConsumerConfig
from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.vm_data import VmData

logger = logging.getLogger(__name__)


class OpenstackConnection:
    """
    Wrapper for Openstack connection, to reduce boilerplate code
    in subsequent functions.
    """

    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = openstack.connect(
            auth_url=ConsumerConfig().openstack_auth_url,
            username=ConsumerConfig().openstack_username,
            password=ConsumerConfig().openstack_password,
            project_name="admin",
            user_domain_name="Default",
            project_domain_name="default",
        )
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


def check_machine_exists(vm_data: VmData) -> bool:
    """
    Checks to see if the machine exists in Openstack.
    """
    with OpenstackConnection() as conn:
        return bool(conn.compute.find_server(vm_data.virtual_machine_id))


def get_server_details(vm_data: VmData) -> Server:
    """
    Gets the server details from Openstack with details included
    """
    with OpenstackConnection() as conn:
        # Workaround for details missing from find_server
        # on the current version of openstacksdk
        found = list(
            conn.compute.servers(uuid=vm_data.virtual_machine_id, all_projects=True)
        )
        if not found:
            raise ValueError(f"Server not found for id: {vm_data.virtual_machine_id}")
        return found[0]


def get_server_networks(vm_data: VmData) -> List[OpenstackAddress]:
    """
    Gets the networks from Openstack for the virtual machine as a list
    of deserialized OpenstackAddresses.
    """
    server = get_server_details(vm_data)
    if "Internal" in server.addresses:
        return OpenstackAddress.get_internal_networks(server.addresses)
    if "Services" in server.addresses:
        return OpenstackAddress.get_services_networks(server.addresses)
    logger.warning("No internal or services network found for server %s", server.name)
    return []


def get_server_metadata(vm_data: VmData) -> dict:
    """
    Gets the metadata from Openstack for the virtual machine.
    """
    server = get_server_details(vm_data)
    return server.metadata


def get_image(vm_data: VmData) -> Optional[Image]:
    """
    Gets the image name from Openstack for the virtual machine.
    """
    server = get_server_details(vm_data)
    uuid = server.image.id
    if not uuid:
        return None

    with OpenstackConnection() as conn:
        image = conn.compute.find_image(uuid)
        return image


def update_metadata(vm_data: VmData, metadata) -> None:
    """
    Updates the metadata for the virtual machine.
    """
    server = get_server_details(vm_data)
    with OpenstackConnection() as conn:
        conn.compute.set_server_metadata(server, **metadata)

    logger.debug("Setting metadata successful")
