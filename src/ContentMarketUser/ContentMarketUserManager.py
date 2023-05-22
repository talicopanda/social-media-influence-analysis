from ContentMarketUser import ContentMarketUser
from ContentMarketConsumer import ContentMarketConsumer
from ContentMarketProducer import ContentMarketProducer
from ContentMarketCoreNode import ContentMarketCoreNode
from user_partitioning.UsersStrategy import UsersStrategy
from UserType import UserType

from typing import Set, List


class ContentMarketUserManager:
    # Attributes
    consumers: Set[ContentMarketConsumer]
    producers: Set[ContentMarketProducer]
    core_nodes: Set[ContentMarketCoreNode]

    def partition_users(self, users: List[ContentMarketUser],
                        partition: UsersStrategy) -> None:
        """Split <users> into consumers, producers, and core nodes
        by <partition>, and store them into class variables.
        """
        for user in users:
            if user.rank < 10:  # 10 top users are core nodes
                core_node = ContentMarketCoreNode(**vars(user))
                self.core_nodes.add(core_node)
            else:
                if partition.is_producer(user):
                    new_prod = ContentMarketProducer(**vars(user))
                    self.producers.add(new_prod)
                if partition.is_consumer(user):
                    new_consumer = ContentMarketConsumer(**vars(user))
                    self.consumers.add(new_consumer)

    def get_user(self, userid: int) -> ContentMarketUser:
        """Return a ContentMarketUser with <userid>.
        """
        # check if it is consumer
        for consumer in self.consumers:
            if consumer.user_id == userid:
                return consumer

        # check if it is producer
        for producer in self.producers:
            if producer.user_id == userid:
                return producer

        # check if it is core node
        for core_node in self.core_nodes:
            if core_node.user_id == userid:
                return core_node

        # if this is not for any user, raise Exception
        raise Exception(f"`{userid}` is not in the list")

    def get_type_users(self, user_type: UserType) -> Set[ContentMarketUser]:
        """Return a set of all users of Type <user_type>.
        """
        if user_type == UserType.CONSUMER:
            return self.consumers
        elif user_type == UserType.PRODUCER:
            return self.producers
        elif user_type == UserType.CORE_NODE:
            return self.core_nodes
        else:
            raise Exception(f"Invalid User Type `{user_type}`")
