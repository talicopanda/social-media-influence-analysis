from abc import ABC, abstractmethod

# classifies everyone has a producer and a consumer
class UserTypeStrategy(ABC):
    def is_consumer(user_id: str) -> bool:
        return True

    def is_producer(user_id: str) -> bool:
        return True