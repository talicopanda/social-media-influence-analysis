from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from User.UserBase import UserBase

core_node_list = [1330571318971027462, 917892794953404417, 23612012, 3161912605,
                  227629567, 919900711, 301042394, 228660231, 2233129128,
                  4369711156, 1884178352, 1651411087, 126345156, 232951413,
                  277594186, 313299656, 186797066, 92284830, 1729528081, 13247182]


class SocialSupportStrategy(UserPartitioningStrategy):
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
        return user.user_id in core_node_list
