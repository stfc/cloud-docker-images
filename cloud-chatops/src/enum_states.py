# pylint: disable=C0114
from enum import Enum, auto


class PRsFoundState(Enum):
    """This Enum provides states for whether any PRs were found."""

    PRS_FOUND = auto()
    NONE_FOUND = auto()
