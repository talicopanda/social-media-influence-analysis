from DAO.MongoDAOBase import MongoDAOBase
from Aggregation.ContentDemandSupply import ContentDemandSupply
from Tweet.ContentMarketTweet import ContentMarketTweet
from User.ContentMarketUser import ContentMarketUser

from typing import Dict, Any, Set
import pymongo


class ContentMarketMongoDAO(MongoDAOBase):
    def load_users(self) -> Set[ContentMarketUser]:
        users = set()
        for user in self.content_market_db[self.market_user_info_collection].find():
            user_dict = {
                "user_id": user["userid"],
                "rank": user["rank"],
                "username": user["username"],
                "influence_one": user["influence one"],
                "influence_two": user["influence two"],
                "production_utility": user["production utility"],
                "consumption_utility": user["consumption utility"],
                "local_follower_count": user["local follower"],
                "local_following_count": user["local following"],
                "local_followers": user["local follower list"],
                "local_following": user["local following list"],
                "global_follower_count": user["global follower"],
                "global_following_count": user["global following"],
                "is_new_user": user["is new user"]
            }
            new_user = ContentMarketUser(**user_dict)
            users.add(new_user)
        return users

    def create_users(self) -> Set[ContentMarketUser]:
        users = set()
        for user in self.community_db[self.community_info_collection].find():
            user_dict = {
                "user_id": user["userid"],
                "rank": user["rank"],
                "username": user["username"],
                "influence_one": user["influence one"],
                "influence_two": user["influence two"],
                "production_utility": user["production utility"],
                "consumption_utility": user["consumption utility"],
                "local_follower_count": user["local follower"],
                "local_following_count": user["local following"],
                "local_followers": user["local follower list"],
                "local_following": user["local following list"],
                "global_follower_count": user["global follower"],
                "global_following_count": user["global following"],
                "is_new_user": user["is new user"]
            }
            new_user = ContentMarketUser(**user_dict)
            users.add(new_user)
        return users

    def _load_tweets(self, db_name: str) -> Set[ContentMarketTweet]:
        tweets = set()
        for tweet in self.content_market_db[db_name].find():
            del tweet["_id"]
            tweets.add(ContentMarketTweet(**tweet))
        return tweets

    def write_mapping_manager(self, name: str,
                              mapping_manager: ContentDemandSupply) -> None:
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

    def store_users(self, users: Set[ContentMarketUser]) -> None:
        # TODO
        pass

    def store_tweets(self, tweets: Set[ContentMarketTweet]) -> None:
        # TODO
        pass
