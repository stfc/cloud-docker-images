# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Tests rabbit messages are consumed correctly from the queue
"""
import json
from typing import Dict

import pytest

from rabbit_consumer.rabbit_message import RabbitMessage


def _example_dict(with_metadata: bool) -> Dict:
    """
    Returns an example dictionary for testing, based on real data from the RabbitMQ queue
    """
    example_dict = {
        "event_type": "compute.instance.create.end",
        "_context_project_name": "project_name",
        "_context_project_id": "project_id",
        "_context_user_name": "user_name",
        "payload": {
            "instance_id": "instance_id",
            "display_name": "vm_name",
            "vcpus": 1,
            "memory_mb": 1024,
            "host": "vm_host",
            "metadata": {},
        },
    }

    if with_metadata:
        example_dict["payload"]["metadata"] = {"AQ_MACHINENAME": "machine_name"}

    return example_dict


@pytest.fixture(name="example_json")
def fixture_example_json():
    """
    Returns an example JSON string for testing, based on real data from the RabbitMQ queue
    """
    return json.dumps(_example_dict(with_metadata=False))


@pytest.fixture(name="example_json_with_metadata")
def fixture_example_json_with_metadata():
    """
    Returns an example JSON string for testing, with metadata included
    """
    return json.dumps(_example_dict(with_metadata=True))


def test_rabbit_json_load(example_json):
    """
    Tests that RabbitMessage.from_json() can load a JSON string and deserialise it into dataclasses
    """
    deserialized = RabbitMessage.from_json(example_json)
    assert deserialized.event_type == "compute.instance.create.end"
    assert deserialized.project_name == "project_name"
    assert deserialized.project_id == "project_id"
    assert deserialized.user_name == "user_name"
    assert deserialized.payload.instance_id == "instance_id"
    assert deserialized.payload.vm_name == "vm_name"
    assert deserialized.payload.vcpus == 1
    assert deserialized.payload.memory_mb == 1024
    assert deserialized.payload.vm_host == "vm_host"


def test_with_metadata(example_json_with_metadata):
    """
    Tests that RabbitMessage.from_json() can load a JSON string and deserialise it into dataclasses
    """
    deserialized = RabbitMessage.from_json(example_json_with_metadata)
    assert deserialized.payload.metadata.machine_name == "machine_name"
