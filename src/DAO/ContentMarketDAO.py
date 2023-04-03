from abc import ABC, abstractmethod
from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketCoreNode import ContentMarketCoreNode
from typing import List, Tuple


class ContentMarketDAO(ABC):
    @abstractmethod
    def load_tweet_embedding(self, tweet_id: int):
        pass

    @abstractmethod
    def load_tweet_embeddinga(self):
        pass

    @abstractmethod
    def load_community_users(self) -> List[ContentMarketUser]:
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

    @abstractmethod
    def load_content_market(self, content_market_id):
        pass

    @abstractmethod
    def write_content_market(self, content_market):
        pass
