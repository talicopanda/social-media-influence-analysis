from enum import Enum


class UserType(Enum):
    CONSUMER = "consumer"
    PRODUCER = "producer"
    CORE_NODE = "core node"
