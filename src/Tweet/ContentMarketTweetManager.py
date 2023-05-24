from Tweet.ContentMarketTweet import ContentMarketTweet
from DAO.ContentMarketDAO import ContentMarketDAO
from User.ContentMarketUserManager import ContentMarketUserManager
from Tweet.TweetType import TweetType

from typing import Set, List
from datetime import datetime


class ContentMarketTweetManager:
    # Attributes (not used yet)
    original_tweets: Set[ContentMarketTweet]
    quotes_of_in_comm: Set[ContentMarketTweet]
    quotes_of_out_comm: Set[ContentMarketTweet]
    retweets_of_in_comm: Set[ContentMarketTweet]
    retweets_of_out_comm: Set[ContentMarketTweet]

    def __init__(self, dao: ContentMarketDAO,
                 user_manager: ContentMarketUserManager):
        print("=================Build Tweets=================")
        # initialize variables
        self.original_tweets = set()
        self.quotes_of_in_comm = set()
        self.quotes_of_out_comm = set()
        self.retweets_of_in_comm = set()
        self.retweets_of_out_comm = set()

        # load tweets into manager
        self._load_tweets(dao, user_manager)
        print("===============Successfully Build TweetManager===============")

    def _load_tweets(self, dao: ContentMarketDAO,
                     user_manager: ContentMarketUserManager):
        """Load <original_tweets>, <quotes_of_in_comm>, <quotes_of_out_comm>,
        <retweets_of_in_comm>, <retweets_of_out_comm> into class variables
        and in <user_manager>"""
        print("=================Build Original Tweets=================")
        for original_tweet in dao.load_original_tweets():
            del original_tweet["_id"]
            tweet = ContentMarketTweet(**original_tweet)
            self.original_tweets.add(tweet)
            user_manager.add_tweet(tweet, TweetType.ORIGINAL_TWEET)

        print("=================Build Quotes of In Community=================")
        for quote_in_community in dao.load_quotes_of_in_community():
            del quote_in_community["_id"]
            tweet = ContentMarketTweet(**quote_in_community)
            self.quotes_of_in_comm.add(tweet)
            user_manager.add_tweet(tweet, TweetType.QUOTE_OF_IN_COMM)

        print("================Build Quotes of Out Community================")
        for quote_out_of_community in dao.load_quotes_of_out_community():
            del quote_out_of_community["_id"]
            tweet = ContentMarketTweet(**quote_out_of_community)
            self.quotes_of_out_comm.add(tweet)
            user_manager.add_tweet(tweet, TweetType.QUOTE_OF_OUT_COMM)

        print("================Build Retweets of In Community================")
        for retweet_in_community in dao.load_retweets_of_in_community():
            del retweet_in_community["_id"]
            tweet = ContentMarketTweet(**retweet_in_community)
            self.retweets_of_in_comm.add(tweet)
            user_manager.add_tweet(tweet, TweetType.RETWEET_OF_IN_COMM)

        print("===============Build Retweets of Out Community===============")
        for retweet_of_out_community in dao.load_retweets_of_out_community():
            del retweet_of_out_community["_id"]
            tweet = ContentMarketTweet(**retweet_of_out_community)
            self.retweets_of_out_comm.add(tweet)
            user_manager.add_tweet(tweet, TweetType.RETWEET_OF_OUT_COMM)

    def get_tweet(self, tweet_id) -> ContentMarketTweet:
        """Return Tweet with <tweet_id>.
        """
        for tweet_group in [self.original_tweets, self.quotes_of_in_comm,
                            self.quotes_of_out_comm, self.retweets_of_in_comm,
                            self.retweets_of_out_comm]:
            for tweet in tweet_group:
                if tweet.id == tweet_id:
                    return tweet

        # if this is not for any tweet, raise Exception
        raise Exception(f"`{tweet_id}` is not in the list")

    def get_tweets(self, tweet_ids: List) -> List[ContentMarketTweet]:
        """Return a list of Tweet with corresponding <tweet_ids>.
        """
        tweet_list = []
        for tweet_id in tweet_ids:
            tweet_list.append(self.get_tweet(tweet_id))
        return tweet_list

    def tweet_created_between_time(self, tweet_id, start_time: datetime, end_time: datetime) -> int:
        """Return 0 if the Tweet with <tweet_id> is not created between
        <start_time> and <end_time>.
        """
        create_time = self.get_tweet(tweet_id).created_at
        return int((start_time <= create_time <= end_time))