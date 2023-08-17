from abc import ABC, abstractmethod

from Aggregation.AggregationBase import AggregationBase
from User.UserBase import UserBase
from Tweet.TweetBase import TweetBase
from Tweet.TweetType import TweetType

from typing import Set


class BuilderBase(ABC):
    @abstractmethod
    def create(self) -> AggregationBase:
        """Create the AggregationBase.
        """
        raise NotImplementedError

    def store(self, aggregation: AggregationBase) -> None:
        """Store the AggregationBase.
        """
        # store users
        self._store_users(
            aggregation.consumers | aggregation.producers | aggregation.core_nodes
        )

        # store tweets
        self._store_tweets(aggregation.original_tweets,
                           TweetType.ORIGINAL_TWEET)
        self._store_tweets(aggregation.retweets_of_in_comm,
                           TweetType.RETWEET_OF_IN_COMM)
        self._store_tweets(aggregation.retweets_of_out_comm,
                           TweetType.RETWEET_OF_OUT_COMM)
        # add retweets of out community by in community
        self._store_tweets(aggregation.retweets_of_out_comm_by_in_comm,
                           TweetType.RETWEET_OF_OUT_COMM_BY_IN_COMM)

    @abstractmethod
    def _store_users(self, users: Set[UserBase]) -> None:
        """A helper function to store users.
        """
        raise NotImplementedError

    @abstractmethod
    def _store_tweets(self, tweets: Set[TweetBase],
                      tweet_type: TweetType) -> None:
        """A helper function to store tweets.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self) -> AggregationBase:
        """Load the AggregationBase from storage.
        """
        raise NotImplementedError
