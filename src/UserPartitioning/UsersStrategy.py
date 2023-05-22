from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy


class UsersStrategy(UserPartitioningStrategy):
    """Classifies user as a producer and a consumer
    """
    def is_consumer(self, user) -> bool:
        return True

    def is_producer(self, user) -> bool:
        return True
