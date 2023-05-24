from abc import ABC, abstractmethod


class UserPartitioningStrategy(ABC):
    @abstractmethod
    def is_consumer(self, user) -> bool:
        """Return True if <user> is a consumer.
        """
        raise NotImplementedError

    @abstractmethod
    def is_producer(self, user) -> bool:
        """Return True if <user> is a producer.
        """
        raise NotImplementedError
