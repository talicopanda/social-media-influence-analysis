from abc import ABC, abstractmethod
from User.ContentMarketUser import ContentMarketUser

from typing import List
import pymongo


class ContentMarketDAO(ABC):
    @abstractmethod
    def load_tweet_embedding(self, tweet_id: int):
        pass

    @abstractmethod
    def load_tweet_embeddings(self):
        pass

    @abstractmethod
    def load_community_users(self) -> pymongo.cursor.Cursor:
        pass

    @abstractmethod
    def load_original_tweets(self) -> pymongo.cursor.Cursor:
        pass

    @abstractmethod
    def load_quotes_of_in_community(self) -> pymongo.cursor.Cursor:
        pass

    @abstractmethod
    def load_quotes_of_out_community(self) -> pymongo.cursor.Cursor:
        pass

    @abstractmethod
    def load_retweets_of_in_community(self) -> pymongo.cursor.Cursor:
        pass

    @abstractmethod
    def load_retweets_of_out_community(self) -> pymongo.cursor.Cursor:
        pass

    @abstractmethod
    def load_content_market(self, content_market_id):
        pass
