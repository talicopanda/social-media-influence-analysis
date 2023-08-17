from __future__ import annotations

from enum import Enum
from typing import Set


def get_all_user_types() -> Set[UserType]:
    """Return a set of all UserType.
    """
    return {UserType.CONSUMER, UserType.PRODUCER, UserType.CORE_NODE}


def value_to_type(value: str) -> UserType:
    for user_type in get_all_user_types():
        if user_type.value == value:
            return user_type


class UserType(Enum):
    """A class that represents different roles of user.
    """
    CONSUMER = "consumer"
    PRODUCER = "producer"
    CORE_NODE = "core_node"
