# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Fixtures for unit tests, used to create mock objects
"""
import uuid

import pytest

from rabbit_consumer.aq_metadata import AqMetadata
from rabbit_consumer.openstack_address import OpenstackAddress
from rabbit_consumer.rabbit_message import RabbitMessage, RabbitMeta, RabbitPayload
from rabbit_consumer.vm_data import VmData


@pytest.fixture(name="image_metadata")
def fixture_image_metadata():
    """
    Creates an ImageMetadata object with mock data
    which represent an example OpenStack image
    """
    return AqMetadata(
        aq_archetype="archetype_mock",
        aq_domain="domain_mock",
        aq_personality="personality_mock",
        aq_os="os_mock",
        aq_os_version="osversion_mock",
    )


@pytest.fixture(name="rabbit_message")
def fixture_rabbit_message():
    """
    Creates a RabbitMessage object with mock data
    """
    rabbit_payload = RabbitPayload(
        instance_id="instance_id_mock",
        memory_mb=1024,
        metadata=RabbitMeta(),
        vcpus=2,
        vm_host="vm_host_mock",
        vm_name="vm_name_mock",
    )

    return RabbitMessage(
        event_type="event_type_mock",
        payload=rabbit_payload,
        project_id="project_id_mock",
        project_name="project_name_mock",
        user_name="user_name_mock",
    )


@pytest.fixture(name="vm_data")
def fixture_vm_data():
    """
    Creates a VmData object with mock data
    """
    return VmData(
        project_id="project_id_mock", virtual_machine_id="virtual_machine_id_mock"
    )


@pytest.fixture(name="openstack_address")
def fixture_openstack_address():
    """
    Creates an OpenstackAddress object with mock data
    """
    return OpenstackAddress(
        addr="127.0.0.123",
        mac_addr="00:00:00:00:00:00",
        version=4,
        hostname=str(uuid.uuid4()),
    )


@pytest.fixture(name="openstack_address_list")
def fixture_openstack_address_list(openstack_address):
    """
    Creates a list of OpenstackAddress objects with mock data
    """
    addresses = [openstack_address, openstack_address]
    for i in addresses:
        # Set a unique hostname for each address, otherwise the fixture
        # will return the same object twice
        i.hostname = str(uuid.uuid4())
    return addresses
