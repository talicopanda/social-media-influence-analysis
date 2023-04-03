from user_partitioning.UserPartitioningStrategy import UserPartitioningStrategy

# classifies everyone has a producer and a consumer
class UsersStrategy(UserPartitioningStrategy):
    def is_consumer(self, user) -> bool:
        return True

    def is_producer(self, user) -> bool:
        return True