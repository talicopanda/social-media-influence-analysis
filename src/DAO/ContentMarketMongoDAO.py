from DAO.ContentMarketDAO import ContentMarketDAO
from User.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMappingManager import ContentMappingManager
from User.UserType import UserType

from typing import List, Dict, Any
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

    def write_mapping_manager(self, name: str,
                              mapping_manager: ContentMappingManager) -> None:
        """Write supply and demand to database.
        """
        # initialize database connection
        output_db = pymongo.MongoClient(self.connection_url)[name]

        # create processable dictionary
        pre_cm_dict = {}

        # convert demand
        for user_type in mapping_manager.demand_spec.keys():
            user_key = user_type.value.replace(" ", "_")
            pre_cm_dict[user_key + "_type_demand"] = mapping_manager.type_demand[user_type]
            pre_cm_dict[user_key + "_agg_demand"] = mapping_manager.agg_demand[user_type]

        # convert supply
        for user_type in mapping_manager.supply_spec.keys():
            user_key = user_type.value.replace(" ", "_")
            pre_cm_dict[user_key + "_type_supply"] = mapping_manager.type_supply[user_type]
            pre_cm_dict[user_key + "_agg_supply"] = mapping_manager.agg_supply[user_type]

        key_map_created = False
        cm_dict = {}
        key_dict = {}
        for key, value in pre_cm_dict.items():
            if not key_map_created:
                key_dict, data_dict = self._create_num_type_mapping(value)
                cm_dict[key] = data_dict
                key_map_created = True
            else:
                cm_dict[key] = self._convert_num_type_mapping(value, key_dict)

        # write to database
        # time stamps
        output_db["time_stamps"].insert_one({
            "time_stamps": mapping_manager.time_stamps
        })
        # ContentType mapping
        output_db["content_type"].insert_many(
            [{key: value} for key, value in key_dict.items()]
        )
        # supply and demand
        for coll_name, data in cm_dict.items():
            output_db[coll_name].insert_one(data)

    def _create_num_type_mapping(self, raw_dict: Dict) -> (Dict[str, Any], Dict):
        """Return a mapping of string '1', '2', '3', ... to keys in <raw_dict>,
        and '1', '2', '3', ... to values in <raw_dict>. The original key-value
        pair correspond to the same key in the return dictionaries.
        """
        acc = "0"
        key_dict = {}
        data_dict = {}
        for key, value in raw_dict.items():
            key_dict[acc] = key
            data_dict[acc] = value
            acc = str(int(acc) + 1)
        return key_dict, data_dict

    def _convert_num_type_mapping(self, raw_dict: Dict, key_dict: Dict[str, Any]) -> Dict:
        """Return a dictionary with <raw_dict>'s keys changed to corresponding
        keys in <key_dict>.
        """
        data_dict = {}
        for key, value in raw_dict.items():
            data_dict[self.get_key_from_value(key_dict, key)] = value
        return data_dict

    def get_key_from_value(self, raw_dict: Dict, value: Any) -> Any:
        """Return the key that maps to <value> in <raw_dict>.
        """
        for k, v in raw_dict.items():
            if v == value:
                return k
