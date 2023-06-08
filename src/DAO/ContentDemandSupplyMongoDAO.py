from DAO.MongoDAOBase import MongoDAOBase
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from User.ContentSpaceUser import ContentSpaceUser

from typing import Set
import pymongo


class ContentDemandSupplyMongoDAO(MongoDAOBase):
    def load_users(self) -> Set[ContentSpaceUser]:
        # TODO
        pass

    def _load_tweets(self, db_name: str) -> Set[ContentSpaceTweet]:
        tweets = set()
        # TODO: use Content Demand Supply DB
        for tweet in self.content_market_db[db_name].find():
            del tweet["_id"]
            tweets.add(ContentSpaceTweet(**tweet))
        return tweets

    def store_users(self, users: Set[ContentSpaceUser]) -> None:
        # TODO
        pass

    def store_tweets(self, tweets: Set[ContentSpaceTweet]) -> None:
        # TODO
        pass
