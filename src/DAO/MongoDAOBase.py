from abc import ABC, abstractmethod

from Tweet.TweetBase import TweetBase
from DAO.DAOBase import DAOBase

from typing import Set, List, Dict
import pymongo


class MongoDAOBase(DAOBase, ABC):
    """
    A parent class for <ContentMarketDAO> and <ContentSpaceDAO>.
    """
    db_type: str
    connection_url: str

    community_db_name: str
    community_info_collection: str
    user_info_collection: str
    original_tweets_collection: str
    quotes_of_in_community_collection: str
    quotes_of_out_community_collection: str
    retweets_of_in_community_collection: str
    retweets_of_out_community_collection: str

    content_market_db_name: str
    clean_original_tweets_collection: str
    clean_replies_collection: str
    clean_quotes_of_in_community_collection: str
    clean_quotes_of_out_community_collection: str
    clean_retweets_of_in_community_collection: str
    clean_retweets_of_out_community_collection: str
    tweet_embeddings_collection: str
    market_user_info_collection: str

    content_space_db_name: str
    content_space_original_tweets_collection: str
    content_space_retweets_of_in_community_collection: str
    content_space_retweets_of_out_community_collection: str
    content_space_user_info: str
    content_space_collection: str

    content_demand_supply_db_name: str

    community_db: any
    content_market_db: any
    content_space_db: any # TODO: change later

    def __init__(self, db_type, connection_url, community_db_name,
                 community_info_collection, user_info_collection,
                 original_tweets_collection, quotes_of_in_community_collection,
                 quotes_of_out_community_collection,
                 retweets_of_in_community_collection,
                 retweets_of_out_community_collection, content_market_db_name,
                 clean_original_tweets_collection, clean_replies_collection,
                 clean_quotes_of_in_community_collection,
                 clean_quotes_of_out_community_collection,
                 clean_retweets_of_in_community_collection,
                 clean_retweets_of_out_community_collection,
                 tweet_embeddings_collection, market_user_info_collection,
                 content_space_db_name, content_space_original_tweets_collection,
                 content_space_retweets_of_in_community_collection,
                 content_space_retweets_of_out_community_collection,
                 content_space_user_info, content_demand_supply_db_name,
                 content_space_collection):
        self.db_type = db_type
        self.connection_url = connection_url
        # Community
        self.community_db_name = community_db_name
        self.community_info_collection = community_info_collection
        self.user_info_collection = user_info_collection
        self.original_tweets_collection = original_tweets_collection
        self.quotes_of_in_community_collection = quotes_of_in_community_collection
        self.quotes_of_out_community_collection = quotes_of_out_community_collection
        self.retweets_of_in_community_collection = retweets_of_in_community_collection
        self.retweets_of_out_community_collection = retweets_of_out_community_collection

        # Content Market
        self.content_market_db_name = content_market_db_name
        self.clean_original_tweets_collection = clean_original_tweets_collection
        self.clean_replies_collection = clean_replies_collection
        self.clean_quotes_of_in_community_collection = clean_quotes_of_in_community_collection
        self.clean_quotes_of_out_community_collection = clean_quotes_of_out_community_collection
        self.clean_retweets_of_in_community_collection = clean_retweets_of_in_community_collection
        self.clean_retweets_of_out_community_collection = clean_retweets_of_out_community_collection
        self.tweet_embeddings_collection = tweet_embeddings_collection
        self.market_user_info_collection = market_user_info_collection

        # Content Space
        self.content_space_db_name = content_space_db_name
        self.content_space_original_tweets_collection = content_space_original_tweets_collection
        self.content_space_retweets_of_in_community_collection = content_space_retweets_of_in_community_collection
        self.content_space_retweets_of_out_community_collection = content_space_retweets_of_out_community_collection
        self.content_space_user_info = content_space_user_info
        self.content_space_collection = content_space_collection

        # Content Demand Supply
        self.content_demand_supply_db_name = content_demand_supply_db_name

        client = pymongo.MongoClient(self.connection_url)
        self.community_db = client[self.community_db_name]
        self.content_market_db = client[self.content_market_db_name]
        self.content_space_db = client[self.content_space_db_name]

    @abstractmethod
    def load_original_tweets(self) -> Set[TweetBase]:
        raise NotImplementedError

    def load_quotes_of_in_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    def load_quotes_of_out_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    def load_retweets_of_in_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    def load_retweets_of_out_community(self) -> Set[TweetBase]:
        raise NotImplementedError

    def load_replies(self) -> Set[TweetBase]:
        raise NotImplementedError

    def load_tweet_embeddings(self) -> Dict[int, List[int]]:
        projection = self.content_market_db[
            self.tweet_embeddings_collection].find({}, {"id": 1, "embedding": 1,
                                                        "_id": 0})
        embeddings = {}
        for p in projection:
            embeddings[p["id"]] = p["embedding"]
        return embeddings
