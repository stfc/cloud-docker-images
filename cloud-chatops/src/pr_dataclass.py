"""
This module declares the dataclass used to store PR information.
This is preferred over dictionaries as dataclasses make code more readable.
"""

from dataclasses import dataclass


@dataclass
class PrData:
    """Class holding information about a single pull request."""

    pr_title: str
    user: str
    url: str
    created_at: str
    draft: bool
    old: bool = False
