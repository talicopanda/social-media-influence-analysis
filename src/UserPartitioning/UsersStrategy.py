from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from User.UserBase import UserBase


class UsersStrategy(UserPartitioningStrategy):
    """Classifies user as a producer, consumer, or core node
    """

    def is_consumer(self, user: UserBase) -> bool:
        """If a user is not a core node, then is a consumer.
        """
        return not self.is_core_node(user)

    def is_producer(self, user: UserBase) -> bool:
        """If a user is not a core node, then is a producer.
        """
        return not self.is_core_node(user)

    def is_core_node(self, user: UserBase) -> bool:
        """If the rank of a user is less than 10, then is a core node.
        """
        return user.rank < 10
