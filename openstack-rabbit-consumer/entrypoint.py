#!/usr/bin/python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2023 United Kingdom Research and Innovation
"""
Prepares the logging and initiates the consumers.
"""
import logging
import logging.handlers
import os
import sys


def _prep_logging():
    logger = logging.getLogger("rabbit_consumer")
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


if __name__ == "__main__":
    _prep_logging()

    from rabbit_consumer.message_consumer import initiate_consumer

    initiate_consumer()
