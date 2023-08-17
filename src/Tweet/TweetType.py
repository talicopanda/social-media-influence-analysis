from enum import Enum


class TweetType(Enum):
    """A class used to identify the types of a tweet.
    """
    ORIGINAL_TWEET = "original tweet"
    QUOTE_OF_IN_COMM = "quote in community"
    QUOTE_OF_OUT_COMM = "quote out community"
    RETWEET_OF_IN_COMM = "retweet in community"
    RETWEET_OF_OUT_COMM = "retweet out community"
    # add retweets of out community by in community
    RETWEET_OF_OUT_COMM_BY_IN_COMM = "retweet out community by in community"
    REPLY = "reply"
