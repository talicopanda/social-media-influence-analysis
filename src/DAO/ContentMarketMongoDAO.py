from DAO.ContentMarketDAO import ContentMarketDAO
from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketCoreNode import ContentMarketCoreNode
from ContentMarket.ContentTweet import ContentTweet
from typing import List
import pymongo


class ContentMarketMongoDAO(ContentMarketDAO):
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
    tweet_embeddings: str
    failed_to_load: int
    community_db: any
    content_market_db: any

    
    def __init__(self, db_type, connection_url, community_db_name, community_info_collection, user_info_collection,
                 original_tweets_collection, quotes_of_in_community_collection, quotes_of_out_community_collection,
                 retweets_of_in_community_collection, retweets_of_out_community_collection, content_market_db_name,
                 clean_original_tweets_collection, clean_replies_collection,
                 clean_quotes_of_in_community_collection, clean_quotes_of_out_community_collection,
                 clean_retweets_of_in_community_collection, clean_retweets_of_out_community_collection,
                 tweet_embeddings):        
        self.db_type = db_type
        self.connection_url = connection_url
        self.community_db_name = community_db_name
        self.community_info_collection = community_info_collection
        self.user_info_collection = user_info_collection
        self.original_tweets_collection = original_tweets_collection
        self.quotes_of_in_community_collection = quotes_of_in_community_collection
        self.quotes_of_out_community_collection = quotes_of_out_community_collection
        self.retweets_of_in_community_collection = retweets_of_in_community_collection
        self.retweets_of_out_community_collection = retweets_of_out_community_collection
        self.content_market_db_name = content_market_db_name
        self.clean_original_tweets_collection = clean_original_tweets_collection
        self.clean_replies_collection = clean_replies_collection
        self.clean_quotes_of_in_community_collection = clean_quotes_of_in_community_collection
        self.clean_quotes_of_out_community_collection = clean_quotes_of_out_community_collection
        self.clean_retweets_of_in_community_collection = clean_retweets_of_in_community_collection
        self.clean_retweets_of_out_community_collection = clean_retweets_of_out_community_collection
        self.tweet_embeddings = tweet_embeddings

        client = pymongo.MongoClient(self.connection_url)
        self.community_db = client[self.community_db_name]
        self.content_market_db = client[self.content_market_db_name]
        self.failed_to_load = 0

    def load_tweet_embedding(self, tweet_id: int) -> List[ContentTweet]:
        embedding = self.db[self.content_tweets_collection_name].find_one({
                                                                          'id': tweet_id})
        if embedding:
            return embedding
        self.failed_to_load += 1

    def load_community_users(self):
        users = self.community_db[self.community_info_collection].find()
        return users

    def load_original_tweets(self) -> List[str]:
        tweets = self.content_market_db[self.clean_original_tweets_collection].find()
        for tweet in tweets:
            print(tweet)
        return tweets

    def load_quotes_of_in_community(self) -> List[str]:
        return self.content_market_db[self.clean_quotes_of_in_community_collection].find()

    def load_quotes_of_out_community(self) -> List[str]:
        return self.content_market_db[self.clean_quotes_of_out_community_collection].find()

    def load_retweets_of_in_community(self) -> List[str]:
        return self.content_market_db[self.clean_retweets_of_in_community_collection].find()

    def load_retweets_of_out_community(self) -> List[str]:
        return self.content_market_db[self.clean_retweets_of_out_community_collection].find()

    def load_content_market(self, content_market_id):
        pass

    def write_content_market(self, content_market):
        pass
