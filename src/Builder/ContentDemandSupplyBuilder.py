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
    space: ContentSpace
    start: datetime
    end: datetime
    period: timedelta

    def __init__(self, *args):
        # create()
        # param: str, ContentDemandSupplyMongoDAO, ContentSpace
        if len(args) == 3:
            self.name = args[0]
            self.dao = args[1]
            self.space = args[2]
        # load()
        # param: str, ContentDemandSupplyMongoDAO
        elif len(args) == 2:
            self.name = args[0]
            self.dao = args[1]

    def create(self) -> ContentDemandSupply:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self.space.original_tweets,
                                  TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self.space.retweets_of_in_comm,
                                  TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self.space.retweets_of_out_comm,
                                  TweetType.RETWEET_OF_OUT_COMM)
        # add retweets of out community by in community
        tweet_manager.load_tweets(self.space.retweets_of_out_comm_by_in_comm, 
                                  TweetType.RETWEET_OF_OUT_COMM_BY_IN_COMM)

        # Build User Manager
        user_manager = UserManager({
            UserType.CONSUMER: self.space.consumers,
            UserType.PRODUCER: self.space.producers,
            UserType.CORE_NODE: self.space.core_nodes
        })

        # Build Content Demand Supply
        ds = ContentDemandSupply(self.name, self.space.content_space,
                                 user_manager, tweet_manager)
        ds.calculate_demand_in_community()
        ds.calculate_demand_out_community()
        # add retweets of out community by in community
        ds.calculate_demand_out_community_by_in_community()
        ds.calculate_supply()
        return ds

    def store(self, ds: ContentDemandSupply) -> None:
        super().store(ds)
        self.dao.init_content_space(ds.content_space)
        self.dao.store_curve("demand_in_community", ds.demand_in_community)
        self.dao.store_curve("demand_out_community", ds.demand_out_community)
        # add retweets of out community by in community
        self.dao.store_curve("demand_out_community_by_in_community", ds.demand_out_community_by_in_community)
        self.dao.store_curve("supply", ds.supply)

    def _store_users(self, users: Set[ContentSpaceUser]) -> None:
        pass

    def _store_tweets(self, tweets: Set[ContentSpaceTweet],
                      tweet_type: TweetType) -> None:
        pass

    def load(self) -> ContentDemandSupply:
        # Build Content Space
        content_space = self.dao.load_content_space()

        # Build Demand and Supply
        demand_in_community = self.dao.load_curve("demand_in_community")
        demand_out_community = self.dao.load_curve("demand_out_community")
        # add retweets of out community by in community
        demand_out_community_by_in_community = self.dao.load_curve("demand_out_community_by_in_community")
        supply = self.dao.load_curve("supply")

        # Build Content Demand Supply
        # add retweets of out community by in community
        return ContentDemandSupply(self.name, content_space, 
                                   demand_in_community, demand_out_community, 
                                   demand_out_community_by_in_community, supply)
