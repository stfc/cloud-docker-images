# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
This file defines the class to handle deserialised metadata for 
Aquilon
"""
import logging
from dataclasses import dataclass
from typing import Dict, Optional

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

logger = logging.getLogger(__name__)


@dataclass
class AqMetadata(DataClassDictMixin):
    """
    Deserialised metadata that is set either on an Openstack image
    or a VM's metadata
    """

    aq_archetype: str
    aq_domain: str

    aq_personality: str
    aq_os_version: str
    aq_os: str

    aq_sandbox: Optional[str] = None

    # pylint: disable=too-few-public-methods
    class Config(BaseConfig):
        """
        Sets the aliases for the metadata keys
        """

        aliases = {
            "aq_archetype": "AQ_ARCHETYPE",
            "aq_domain": "AQ_DOMAIN",
            "aq_sandbox": "AQ_SANDBOX",
            "aq_personality": "AQ_PERSONALITY",
            "aq_os_version": "AQ_OSVERSION",
            "aq_os": "AQ_OS",
        }

    def override_from_vm_meta(self, vm_meta: Dict[str, str]):
        """
        Overrides the values in the metadata with the values from the VM's
        metadata
        """
        for attr, alias in self.Config.aliases.items():
            if alias in vm_meta:
                setattr(self, attr, vm_meta[alias])
