from User.UserBase import UserBase
from Tweet.TweetBase import TweetBase
from User.UserManager import UserManager
from Tweet.TweetManager import TweetManager

from typing import Set, Optional


class AggregationBase:
    """
    A class that represents the content market and calculates information about
    users/tweets demands, supplies and causation
    """

    name: str
    consumers: Set[UserBase]
    producers: Set[UserBase]
    core_nodes: Set[UserBase]

    original_tweets: Set[TweetBase]
    retweets_of_in_comm: Set[TweetBase]
    retweets_of_out_comm: Set[TweetBase]

    def __init__(self, name: str, user_manager: UserManager,
                 tweet_manager: Optional[TweetManager]):
        self.name = name

        # store users
        self.consumers = user_manager.consumers
        self.producers = user_manager.producers
        self.core_nodes = user_manager.core_nodes

        # store tweets
        self.original_tweets = tweet_manager.original_tweets
        self.retweets_of_in_comm = tweet_manager.retweets_of_in_comm
        self.retweets_of_out_comm = tweet_manager.retweets_of_out_comm
