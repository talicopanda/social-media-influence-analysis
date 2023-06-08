from Tweet.TweetType import TweetType
from Tweet.TweetBase import TweetBase

from typing import Set, List


class TweetManager:
    # Attributes (not used yet)
    original_tweets: Set[TweetBase]
    quotes_of_in_comm: Set[TweetBase]
    quotes_of_out_comm: Set[TweetBase]
    retweets_of_in_comm: Set[TweetBase]
    retweets_of_out_comm: Set[TweetBase]
    replies: Set[TweetBase]

    def __init__(self):
        print("=================Build Tweets=================")
        # initialize variables
        self.original_tweets = set()
        self.quotes_of_in_comm = set()
        self.quotes_of_out_comm = set()
        self.retweets_of_in_comm = set()
        self.retweets_of_out_comm = set()
        self.replies = set()
        print("===============Successfully Build TweetManager===============")

    def load_tweets(self, tweets: Set[TweetBase], tweet_type: TweetType):
        """Load <original_tweets>, <quotes_of_in_comm>, <quotes_of_out_comm>,
        <retweets_of_in_comm>, <retweets_of_out_comm> into class variables
        and in <user_manager>"""
        if tweet_type == TweetType.ORIGINAL_TWEET:
            self.original_tweets = tweets
        elif tweet_type == TweetType.QUOTE_OF_IN_COMM:
            self.quotes_of_in_comm = tweets
        elif tweet_type == TweetType.QUOTE_OF_OUT_COMM:
            self.quotes_of_out_comm = tweets
        elif tweet_type == TweetType.RETWEET_OF_IN_COMM:
            self.retweets_of_in_comm = tweets
        elif tweet_type == TweetType.RETWEET_OF_OUT_COMM:
            self.retweets_of_out_comm = tweets
        elif tweet_type == TweetType.REPLY:
            self.replies = tweets
        else:
            raise Exception(f"Invalid Tweet Type `{tweet_type}` when getting")

    def get_tweet(self, tweet_id: int) -> TweetBase:
        """Return Tweet with <tweet_id>.
        """
        for tweet_group in [self.original_tweets, self.quotes_of_in_comm,
                            self.quotes_of_out_comm, self.retweets_of_in_comm,
                            self.retweets_of_out_comm, self.replies]:
            for tweet in tweet_group:
                if tweet.id == tweet_id:
                    return tweet

        # if this is not for any tweet, raise Exception
        raise Exception(f"`{tweet_id}` is not in the list")

    def get_tweets(self, tweet_ids: List[int]) -> List[TweetBase]:
        """Return a list of Tweet with corresponding <tweet_ids>.
        """
        tweet_list = []
        for tweet_id in tweet_ids:
            tweet_list.append(self.get_tweet(tweet_id))
        return tweet_list

    def get_type_tweets(self, tweet_type: TweetType) -> Set[TweetBase]:
        """Return a set of all Tweets with <tweet_type>.
        """
        if tweet_type == TweetType.ORIGINAL_TWEET:
            return self.original_tweets
        elif tweet_type == TweetType.QUOTE_OF_IN_COMM:
            return self.quotes_of_in_comm
        elif tweet_type == TweetType.QUOTE_OF_OUT_COMM:
            return self.quotes_of_out_comm
        elif tweet_type == TweetType.RETWEET_OF_IN_COMM:
            return self.retweets_of_in_comm
        elif tweet_type == TweetType.RETWEET_OF_OUT_COMM:
            return self.retweets_of_out_comm
        elif tweet_type == TweetType.REPLY:
            return self.replies
        else:
            raise Exception(f"Invalid Tweet Type `{tweet_type}` when getting")

