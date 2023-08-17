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
    # add retweets of out community by in community
    retweets_of_out_comm_by_in_comm: Set[TweetBase]

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
        # add retweets of out community by in community
        self.retweets_of_out_comm_by_in_comm = tweet_manager.retweets_of_out_comm_by_in_comm
    
    def get_tweet(self, id) -> TweetBase:
        """Return the tweet with <id>."""
        for tweet in self.original_tweets:
            if tweet.id == id:
                return tweet
        for tweet in self.retweets_of_in_comm:
            if tweet.id == id:
                return tweet
        for tweet in self.retweets_of_out_comm:
            if tweet.id == id:
                return tweet
        # add retweets of out community by in community
        for tweet in self.retweets_of_out_comm_by_in_comm:
            if tweet.id == id:
                return tweet
    
    def get_user(self, id) -> UserBase:
        """Return the user with <id>."""
        for user in self.consumers:
            if user.user_id == id:
                return user
        for user in self.producers:
            if user.user_id == id:
                return user
        for user in self.core_nodes:
            if user.user_id == id:
                return user
