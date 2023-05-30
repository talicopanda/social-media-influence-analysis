from enum import Enum


def get_tweet_type(tweet_str: str):
    """Return the TweetType of corresponding string <tweet_str>.
    """
    for tweet_type in TweetType.__members__.values():
        if tweet_type.value == tweet_str:
            return tweet_type
    raise ValueError(f"Invalid tweet type with representation: {tweet_str}")


class TweetType(Enum):
    ORIGINAL_TWEET = "original tweet"
    QUOTE_OF_IN_COMM = "quote in community"
    QUOTE_OF_OUT_COMM = "quote out community"
    RETWEET_OF_IN_COMM = "retweet in community"
    RETWEET_OF_OUT_COMM = "retweet out community"
    REPLY = "reply"
