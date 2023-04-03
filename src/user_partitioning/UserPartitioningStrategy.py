from abc import ABC, abstractmethod

class UserPartitioningStrategy(ABC):
    @abstractmethod
    def is_consumer(self, user) -> bool:
        pass

    @abstractmethod
    def is_producer(self, user) -> bool:
        pass