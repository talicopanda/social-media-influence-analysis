from abc import ABC, abstractmethod

from Aggregation.AggregationBase import AggregationBase
from User.UserBase import UserBase
from Tweet.TweetBase import TweetBase

from typing import Set


class BuilderBase(ABC):
    @abstractmethod
    def create(self) -> AggregationBase:
        raise NotImplementedError

    def store(self, aggregation: AggregationBase) -> None:
        # store users
        self._store_users(aggregation.consumers)
        self._store_users(aggregation.producers)
        self._store_users(aggregation.core_nodes)

        # store tweets
        self._store_tweets(aggregation.original_tweets)
        self._store_tweets(aggregation.retweets_of_in_comm)
        self._store_tweets(aggregation.retweets_of_out_comm)

    @abstractmethod
    def _store_users(self, users: Set[UserBase]) -> None:
        raise NotImplementedError

    @abstractmethod
    def _store_tweets(self, tweets: Set[TweetBase]) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self) -> AggregationBase:
        raise NotImplementedError
