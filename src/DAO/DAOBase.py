from abc import ABC, abstractmethod

from Tweet.TweetBase import TweetBase
from User.UserBase import UserBase

from typing import Set


class DAOBase(ABC):
    """
    A parent class for <MongoDAOBase>.
    """
    @abstractmethod
    def load_users(self) -> Set[UserBase]:
        raise NotImplementedError

    @abstractmethod
    def load_original_tweets(self) -> Set[TweetBase]:
        raise NotImplementedError

    @abstractmethod
    def load_quotes_of_in_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    @abstractmethod
    def load_quotes_of_out_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    @abstractmethod
    def load_retweets_of_in_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    @abstractmethod
    def load_retweets_of_out_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    @abstractmethod
    def load_replies(self) -> Set[TweetBase]:
        raise NotImplementedError

    @abstractmethod
    def load_tweet_embeddings(self):
        raise NotImplementedError

    @abstractmethod
    def store_users(self, users: Set[UserBase]) -> None:
        raise NotImplementedError

    @abstractmethod
    def store_tweets(self, tweets: Set[TweetBase]) -> None:
        raise NotImplementedError
