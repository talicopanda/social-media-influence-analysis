from ContentMarketUser import ContentMarketUser
from ContentMarketConsumer import ContentMarketConsumer
from ContentMarketProducer import ContentMarketProducer
from ContentMarketCoreNode import ContentMarketCoreNode
from UserType import UserType

from typing import Set


class ContentMarketUserManager:
    # Attributes
    consumers: Set[ContentMarketConsumer]
    producers: Set[ContentMarketProducer]
    core_nodes: Set[ContentMarketCoreNode]

    def __init__(self, users: Set[ContentMarketUser]):
        self._role_split(users)

    def _role_split(self, users: Set[ContentMarketUser]):
        """Split users into consumers, producers, and core nodes.
        """
        for user in users:
            if isinstance(user, ContentMarketConsumer):
                self.consumers.add(user)
            if isinstance(user, ContentMarketProducer):
                self.producers.add(user)
            if isinstance(user, ContentMarketCoreNode):
                self.core_nodes.add(user)

    def get_users(self, user_type: UserType) -> Set[ContentMarketUser]:
        """Return
        """
        if user_type == UserType.CONSUMER:
            return self.consumers
        elif user_type == UserType.PRODUCER:
            return self.producers
        elif user_type == UserType.CORE_NODE:
            return self.core_nodes
        else:
            raise Exception("Invalid User Type")
