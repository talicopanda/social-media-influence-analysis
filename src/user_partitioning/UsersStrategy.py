from user_partitioning.UserPartitioningStrategy import UserPartitioningStrategy


class UsersStrategy(UserPartioningStrategy):
    """
    Classifies everyone as a producer and a consumer
    """

    def is_consumer(self, user) -> bool:
        return True

    def is_producer(self, user) -> bool:
        return True
