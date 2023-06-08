from abc import ABC, abstractmethod

from User.UserBase import UserBase


class UserPartitioningStrategy(ABC):
    @abstractmethod
    def is_consumer(self, user: UserBase) -> bool:
        """Return True if <user> is a consumer.
        """
        raise NotImplementedError

    @abstractmethod
    def is_producer(self, user: UserBase) -> bool:
        """Return True if <user> is a producer.
        """
        raise NotImplementedError

    @abstractmethod
    def is_core_node(self, user: UserBase) -> bool:
        raise NotImplementedError
