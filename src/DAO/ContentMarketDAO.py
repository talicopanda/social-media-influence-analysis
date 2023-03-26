from abc import ABC, abstractmethod
from ..ContentMarket.ContentMarketUser import ContentMarketUser
from ..ContentMarket.ContentMarketCoreNode import ContentMarketCoreNode
from ..ContentMarket.ContentTweet import ContentTweet
from typing import List, Tuple


class ContentMarketDAO(ABC):
    @abstractmethod
    def load_tweet_embedding(self, tweet_id: int) -> List[ContentTweet]:
        pass

    @abstractmethod
    def load_users(self) -> List[ContentMarketUser]:
        pass

    @abstractmethod
    def load_user_tweet_ids(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def load_user_tweet_ids(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def load_user_retweet_ids(self, user_id: str) -> List[str]:
        pass

    @abstractmethod
    def load_user_retweet_in_community_ids(self, user_id: str) -> List[str]:
        pass

    # TODO: get rid of this if we handle core node detection ourselves
    @abstractmethod
    def load_core_nodes(self) -> List[ContentMarketCoreNode]:
        pass

    @abstractmethod
    def load_content_market(self, content_market_id):
        pass

    @abstractmethod
    def write_content_market(self, content_market):
        pass
