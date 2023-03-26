from UserPartitioningStrategy import UserPartioningStrategy

# classifies everyone has a producer and a consumer
class UsersStrategy(UserPartioningStrategy):
    def is_consumer(self, user) -> bool:
        return True

    def is_producer(self, user) -> bool:
        return True