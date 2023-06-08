from Builder.BuilderBase import BuilderBase
from Tweet.TweetManager import TweetManager
from Tweet.TweetType import TweetType
from DAO.ContentMarketMongoDAO import ContentMarketMongoDAO
from User.UserManager import UserManager
from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from Aggregation.ContentMarket import ContentMarket
from User.ContentMarketUser import ContentMarketUser
from Tweet.ContentMarketTweet import ContentMarketTweet

from typing import Set


class ContentMarketBuilder(BuilderBase):
    name: str
    dao: ContentMarketMongoDAO
    partition: UserPartitioningStrategy

    def __init__(self, name: str, dao: ContentMarketMongoDAO,
                 partition: UserPartitioningStrategy):
        self.name = name
        self.dao = dao
        self.partition = partition

    def create(self) -> ContentMarket:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self.dao.load_original_tweets(),
                                  TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self.dao.load_retweets_of_in_community(),
                                  TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self.dao.load_retweets_of_out_community(),
                                  TweetType.RETWEET_OF_OUT_COMM)

        # Build User Manager
        user_manager = UserManager(self.dao.create_users(),
                                   self.partition, tweet_manager)

        # Build Content Market
        return ContentMarket(self.name, user_manager, tweet_manager)

    def _store_users(self, users: Set[ContentMarketUser]) -> None:
        self.dao.store_users(users)

    def _store_tweets(self, tweets: Set[ContentMarketTweet]) -> None:
        self.dao.store_tweets(tweets)

    def load(self) -> ContentMarket:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self.dao.load_original_tweets(),
                                  TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self.dao.load_retweets_of_in_community(),
                                  TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self.dao.load_retweets_of_out_community(),
                                  TweetType.RETWEET_OF_OUT_COMM)

        # Build User Manager
        user_manager = UserManager(self.dao.load_users(),
                                   self.partition, tweet_manager)

        # Build Content Market
        return ContentMarket(self.name, user_manager, tweet_manager)
