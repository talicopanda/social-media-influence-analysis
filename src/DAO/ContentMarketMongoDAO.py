from DAO.ContentMarketDAO import ContentMarketDAO
from ContentMarketUser.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarket import ContentMarket
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
    tweet_embeddings_collection: str
    failed_to_load: int
    community_db: any
    content_market_db: any

    def __init__(self, db_type, connection_url, community_db_name, community_info_collection, user_info_collection,
                 original_tweets_collection, quotes_of_in_community_collection, quotes_of_out_community_collection,
                 retweets_of_in_community_collection, retweets_of_out_community_collection, content_market_db_name,
                 clean_original_tweets_collection, clean_replies_collection,
                 clean_quotes_of_in_community_collection, clean_quotes_of_out_community_collection,
                 clean_retweets_of_in_community_collection, clean_retweets_of_out_community_collection,
                 tweet_embeddings_collection):
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
        self.tweet_embeddings_collection = tweet_embeddings_collection

        client = pymongo.MongoClient(self.connection_url)
        self.community_db = client[self.community_db_name]
        self.content_market_db = client[self.content_market_db_name]
        self.failed_to_load = 0

    def load_tweet_embedding(self, tweet_id: int):
        embedding = self.content_market_db[self.tweet_embeddings_collection].find_one({
                                                                          'id': tweet_id})
        if embedding:
            return embedding
        self.failed_to_load += 1

    def load_community_users(self):
        users = self.community_db[self.community_info_collection].find()
        return users

    def load_tweet_embeddings(self):
        projection = self.content_market_db[self.tweet_embeddings_collection].find({}, { "id": 1, "embedding": 1, "_id": 0 })
        embeddings = {}
        for p in projection:
            embeddings[p["id"]] = p["embedding"]
        return embeddings

    def load_users(self) -> List[ContentMarketUser]:
        print("This function is never used")
        users = self.db[self.content_market_users_collection_name].find()
        return users

    def load_original_tweets(self) -> pymongo.cursor.Cursor:
        tweets = self.content_market_db[self.clean_original_tweets_collection].find()
        return tweets

    def load_quotes_of_in_community(self) -> pymongo.cursor.Cursor:
        return self.content_market_db[self.clean_quotes_of_in_community_collection].find()

    def load_quotes_of_out_community(self) -> pymongo.cursor.Cursor:
        return self.content_market_db[self.clean_quotes_of_out_community_collection].find()

    def load_retweets_of_in_community(self) -> pymongo.cursor.Cursor:
        return self.content_market_db[self.clean_retweets_of_in_community_collection].find()

    def load_retweets_of_out_community(self) -> pymongo.cursor.Cursor:
        return self.content_market_db[self.clean_retweets_of_out_community_collection].find()

    def load_content_market(self, content_market_name):
        return self.content_market_db[self.content_market_output_db].find_one({"name": content_market_name})

    def write_content_market(self, content_market: ContentMarket):
        cm_dict = vars(content_market)

        # in case a user is both a producer and consumer,
        # we can't convert the object twice
        converted_users = set()

        # convert nest objects into dictionaries to write out as json to mongo
        def serialize_user_fields(user_type: str):
            for j in range(len(cm_dict[user_type][i]["original_tweets"])):
                cm_dict[user_type][i]["original_tweets"][j] = vars(cm_dict[user_type][i]["original_tweets"][j])
            for j in range(len(cm_dict[user_type][i]["quotes_of_in_community"])):
                cm_dict[user_type][i]["quotes_of_in_community"][j] = vars(cm_dict[user_type][i]["quotes_of_in_community"][j])
            for j in range(len(cm_dict[user_type][i]["quotes_of_out_community"])):
                cm_dict[user_type][i]["quotes_of_out_community"][j] = vars(cm_dict[user_type][i]["quotes_of_out_community"][j])
            for j in range(len(cm_dict[user_type][i]["retweets_of_in_community"])):
                cm_dict[user_type][i]["retweets_of_in_community"][j] = vars(cm_dict[user_type][i]["retweets_of_in_community"][j])
            for j in range(len(cm_dict[user_type][i]["retweets_of_out_community"])):
                cm_dict[user_type][i]["retweets_of_out_community"][j] = vars(cm_dict[user_type][i]["retweets_of_out_community"][j])


        for i in range(len(cm_dict["consumers"])):
            cm_dict["consumers"][i] = vars(cm_dict["consumers"][i])
            converted_users.add(cm_dict["consumers"][i]["user_id"])
            serialize_user_fields("consumers")


        for i in range(len(cm_dict["producers"])):
            cm_dict["producers"][i] = vars(cm_dict["producers"][i])
            if cm_dict["producers"][i]["user_id"] in converted_users:
                continue
            serialize_user_fields("producers")

        # Note: this assumes that a core node cannot also be a producer or consumer
        for i in range(len(cm_dict["core_nodes"])):
            cm_dict["core_nodes"][i] = vars(cm_dict["core_nodes"][i])
            serialize_user_fields("core_nodes")

        cm_dict["clustering"] = vars(cm_dict["clustering"])

        output_db = pymongo.MongoClient(self.connection_url)[content_market.name]
        output_db["core_nodes"].insert_many(cm_dict["core_nodes"])
        output_db["consumers"].insert_many(cm_dict["consumers"])
        output_db["producers"].insert_many(cm_dict["producers"])
        output_db["clustering"].insert_one(cm_dict["clustering"])


