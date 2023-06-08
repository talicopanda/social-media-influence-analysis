from Builder.BuilderBase import BuilderBase
from Tweet.TweetManager import TweetManager
from Tweet.TweetType import TweetType
from DAO.ContentDemandSupplyMongoDAO import ContentDemandSupplyMongoDAO
from User.UserManager import UserManager
from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from Aggregation.ContentSpace import ContentSpace
from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType

from typing import Set
from datetime import timedelta


class ContentDemandSupplyBuilder(BuilderBase):
    name: str
    dao: ContentDemandSupplyMongoDAO
    partition: UserPartitioningStrategy
    space: ContentSpace
    period: timedelta

    def __init__(self, *args):
        # param: str, ContentDemandSupplyMongoDAO, UserPartitioningStrategy
        if len(args) == 3:
            self.name = args[0]
            self.dao = args[1]
            self.partition = args[2]
        # param: str, ContentDemandSupplyMongoDAO, ContentSpace, timedelta
        elif len(args) == 4:
            self.name = args[0]
            self.dao = args[1]
            self.space = args[2]
            self.period = args[3]

    def create(self) -> ContentDemandSupply:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self.space.original_tweets,
                                  TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self.space.retweets_of_in_comm,
                                  TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self.space.retweets_of_out_comm,
                                  TweetType.RETWEET_OF_OUT_COMM)

        # Build User Manager
        user_manager = UserManager({
            UserType.CONSUMER: self.space.consumers,
            UserType.PRODUCER: self.space.producers,
            UserType.CORE_NODE: self.space.core_nodes
        })

        # Build Content Space
        ds = ContentDemandSupply(self.name, self.space.content_space,
                                 user_manager, tweet_manager, self.period)
        ds.calculate_user_demand()
        ds.calculate_user_supply()
        ds.calculate_user_agg_mapping()
        return ds

    def _store_users(self, users: Set[ContentSpaceUser]) -> None:
        self.dao.store_users(users)

    def _store_tweets(self, tweets: Set[ContentSpaceTweet]) -> None:
        self.dao.store_tweets(tweets)

    def load(self) -> ContentSpace:
        # TODO
        pass
