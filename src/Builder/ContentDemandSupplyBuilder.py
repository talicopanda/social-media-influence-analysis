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
from datetime import datetime, timedelta


class ContentDemandSupplyBuilder(BuilderBase):
    name: str
    dao: ContentDemandSupplyMongoDAO
    partition: UserPartitioningStrategy
    space: ContentSpace
    start: datetime
    end: datetime
    period: timedelta

    def __init__(self, *args):
        # param: str, ContentDemandSupplyMongoDAO, UserPartitioningStrategy
        if len(args) == 3:
            self.name = args[0]
            self.dao = args[1]
            self.partition = args[2]
        # param: str, ContentDemandSupplyMongoDAO, ContentSpace,
        #        datetime, datetime, timedelta
        elif len(args) == 6:
            self.name = args[0]
            self.dao = args[1]
            self.space = args[2]
            self.start = args[3]
            self.end = args[4]
            self.period = args[5]

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

        # Build Content Demand Supply
        ds = ContentDemandSupply(self.name, self.space.content_space,
                                 user_manager, tweet_manager,
                                 self.start, self.end, self.period)
        ds.calculate_user_demand()
        ds.calculate_user_supply()
        ds.calculate_user_agg_mapping()
        return ds

    def store(self, ds: ContentDemandSupply) -> None:
        super().store(ds)
        self.dao.init_content_space(ds.content_space)
        self.dao.store_time_stamps(ds.time_stamps)
        self.dao.store_curve({"user_demand": ds.user_demand})
        self.dao.store_curve({"user_supply": ds.user_supply})
        self.dao.store_curve({"user_agg_demand": ds.user_agg_demand})
        self.dao.store_curve({"user_agg_supply": ds.user_agg_supply})

    def _store_users(self, users: Set[ContentSpaceUser]) -> None:
        self.dao.store_users(users)

    def _store_tweets(self, tweets: Set[ContentSpaceTweet],
                      tweet_type: TweetType) -> None:
        self.dao.store_tweets(tweets, tweet_type)

    def load(self) -> ContentDemandSupply:
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

        # Build time stamps
        time_stamps = self.dao.load_time_stamps()

        # Build Demand and Supply
        user_demand = self.dao.load_curve("user_demand")
        user_supply = self.dao.load_curve("user_supply")
        user_agg_demand = self.dao.load_curve("user_agg_demand")
        user_agg_supply = self.dao.load_curve("user_agg_supply")

        # Build Content Demand Supply
        return ContentDemandSupply(self.name, user_manager, tweet_manager,
                                   time_stamps, user_demand, user_supply,
                                   user_agg_demand, user_agg_supply)
