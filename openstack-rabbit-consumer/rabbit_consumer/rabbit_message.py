# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
This file handles how messages from Rabbit are processed and the 
message extracted
"""
from dataclasses import dataclass, field
from typing import Optional

from mashumaro import field_options
from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class MessageEventType(DataClassJSONMixin):
    """
    Parses a raw message from RabbitMQ to determine the event_type
    """

    event_type: str


@dataclass
class RabbitMeta(DataClassJSONMixin):
    """
    Deserialised custom VM metadata
    """

    machine_name: Optional[str] = field(
        metadata=field_options(alias="AQ_MACHINENAME"), default=None
    )


@dataclass
# pylint: disable=too-many-instance-attributes
class RabbitPayload(DataClassJSONMixin):
    """
    Deserialises the payload of a RabbitMQ message
    """

    instance_id: str
    vm_name: str = field(metadata=field_options(alias="display_name"))
    vcpus: int
    memory_mb: int
    vm_host: str = field(metadata=field_options(alias="host"))

    metadata: RabbitMeta


@dataclass
class RabbitMessage(DataClassJSONMixin):
    """
    Deserialised RabbitMQ message
    """

    event_type: str
    project_name: str = field(metadata=field_options(alias="_context_project_name"))
    project_id: str = field(metadata=field_options(alias="_context_project_id"))
    user_name: str = field(metadata=field_options(alias="_context_user_name"))
    payload: RabbitPayload
