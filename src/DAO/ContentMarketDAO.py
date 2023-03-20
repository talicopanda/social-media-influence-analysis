from abc import ABC, abstractmethod
from ContentMarketUser import ContentMarketUser
from ContentMarket import ContentMarket
from ContentMarketCoreNode import ContentMarketCoreNode
from ContentTweet import ContentTweet
from typing import List, Tuple


class ContentMarketDAO(ABC):

    @abstractmethod
    def __init__(self, config):
        pass
        
    @abstractmethod
    def load_content_tweets(self) -> List[ContentTweet]:
        pass

    @abstractmethod
    def write_content_tweets(self, content_tweets: List[ContentTweet]):
        pass

    @abstractmethod
    def load_content_market_users(self) -> List[ContentMarketUser]:
        pass

    @abstractmethod
    def write_content_market_users(self, users: List[ContentMarketUser]):
        pass

    @abstractmethod
    def load_core_nodes(self) -> List[ContentMarketCoreNode]:
        pass

    @abstractmethod
    def write_core_nodes(self, core_nodes: ContentMarketCoreNode) -> List[ContentMarketCoreNode]:
        pass

    @abstractmethod
    def load_content_market(self) -> ContentMarket:
        pass

    @abstractmethod
    def write_content_market(self, ContentMarket):
        pass

