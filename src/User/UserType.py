from __future__ import annotations

from enum import Enum
from typing import Set


def get_all_user_types() -> Set[UserType]:
    """Return a set of all UserType.
    """
    return {UserType.CONSUMER, UserType.PRODUCER, UserType.CORE_NODE}


class UserType(Enum):
    CONSUMER = "consumer"
    PRODUCER = "producer"
    CORE_NODE = "core node"
