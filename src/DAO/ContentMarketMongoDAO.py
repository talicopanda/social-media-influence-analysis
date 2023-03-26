from ContentMarketDAO import ContentMarketDAO
from ContentMarketUser import ContentMarketUser
from ContentMarketCoreNode import ContentMarketCoreNode
from ContentTweet import ContentTweet
from typing import List
import pymongo

class ContentMarketMongoDAO(ContentMarketDAO):
    content_tweets_collection_name: str
    content_market_users_collection_name: str
    core_nodes_collection_name: str
    db_client: any # TODO: change this type and get pipenv working
    failed_to_load: int


    def __init__(self, db_name, users_collection, content_tweets_collection):
        self.content_tweets_collection_name = content_tweets_collection
        self.content_market_users_collection_name = users_collection

        client = pymongo.MongoClient()
        self.db = client[db_name]
        self.failed_to_load = 0

    def load_tweet_embedding(self, tweet_id: int) -> List[ContentTweet]:
        embedding = self.db[self.content_tweets_collection_name].find_one({'id': tweet_id})
        if embedding:
            return embedding
        self.failed_to_load += 1

    def load_users(self) -> List[ContentMarketUser]:
        users = self.db[self.content_market_users_collection_name].find()
        return users

    def load_user_tweet_ids(self, user_id: str) -> List[str]:
        pass

    def load_user_tweet_ids(self, user_id: str) -> List[str]:
        pass

    def load_user_retweet_ids(self, user_id: str) -> List[str]:
        pass

    def load_user_retweet_in_community_ids(self, user_id: str) -> List[str]:
        pass

    def load_core_nodes(self) -> List[ContentMarketCoreNode]:
        pass

    def load_content_market(self, content_market_id):
        pass
    
    def write_content_market(self, content_market):
        pass