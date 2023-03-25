from abc import ABC, abstractmethod

from UsersStrategy import UsersStrategy

class UserPartioningStrategy(ABC):
    @abstractmethod
    def is_consumer(user_id: str) -> bool:
        pass

    @abstractmethod
    def is_producer(user_id: str) -> bool:
        pass

UserPartioningStrategy.register(UsersStrategy)