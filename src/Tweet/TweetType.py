from enum import Enum


class TweetType(Enum):
    ORIGINAL_TWEET = "original tweet"
    QUOTE_OF_IN_COMM = "quote in community"
    QUOTE_OF_OUT_COMM = "quote out community"
    RETWEET_OF_IN_COMM = "retweet in community"
    RETWEET_OF_OUT_COMM = "retweet out community"
    REPLY = "reply"
