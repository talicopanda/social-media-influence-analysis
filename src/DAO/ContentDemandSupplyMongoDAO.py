from DAO.MongoDAOBase import MongoDAOBase
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.TweetType import TweetType
from Mapping.ContentType import ContentType

from typing import Set, List, Dict, Any, Union
from copy import deepcopy
from datetime import datetime

# file global variable
content_space = set()
repr_to_num = dict()


def _convert_tweet(tweet: ContentSpaceTweet) -> Dict[str, Any]:
    tweet_dict = deepcopy(vars(tweet))
    tweet_dict["content"] = tweet.content.get_representation()
    return tweet_dict


def _serialize_space_tweet(tweets: Set[ContentSpaceTweet]) \
        -> List[Dict[str, Any]]:
    return [_convert_tweet(tweet) for tweet in tweets]


def _populate_content_type(representation: Any,
                           content_type_set: Set[ContentType]) -> ContentType:
    """A helper function returning the ContentType with <representation>.
    If there also exists such ContentType in <content_type_set>, return it;
    else create a new ContentType with <representation>, store in
    <content_type_set>, and return the new one.
    """
    for content_type in content_type_set:
        if content_type.representation == representation:
            # this means that such ContentType has been created,
            # so return the object
            return content_type

    # else create the content type and return the new object
    new_type = ContentType(representation)
    content_type_set.add(new_type)
    return new_type


class ContentDemandSupplyMongoDAO(MongoDAOBase):
    def load_users(self) -> Set[ContentSpaceUser]:
        users = set()
        for user in self.content_demand_supply_db[
            self.content_ds_user_info].find():
            user_dict = {
                "user_id": user["user_id"],
                "rank": user["rank"],
                "username": user["username"],
                "influence_one": user["influence_one"],
                "influence_two": user["influence_two"],
                "production_utility": user["production_utility"],
                "consumption_utility": user["consumption_utility"],
                "local_follower_count": user["local_follower_count"],
                "local_following_count": user["local_following_count"],
                "local_followers": user["local_followers"],
                "local_following": user["local_following"],
                "global_follower_count": user["global_follower_count"],
                "global_following_count": user["global_following_count"],
                "is_new_user": user["is_new_user"]
            }
            new_user = ContentSpaceUser(**user_dict)
            users.add(new_user)
        return users

    def _load_tweets(self, db_name: str) -> Set[ContentSpaceTweet]:
        tweets = set()
        for tweet in self.content_demand_supply_db[db_name].find():
            del tweet["_id"]
            tweet["text"] = _populate_content_type(tweet["content"],
                                                   content_space)
            tweet.pop("content")
            tweets.add(ContentSpaceTweet(**tweet))
        return tweets

    def load_original_tweets(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(self.content_ds_original_tweets_collection)

    def load_quotes_of_in_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_quotes_of_out_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_retweets_of_in_community(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(
            self.content_ds_retweets_of_in_community_collection)

    def load_retweets_of_out_community(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(
            self.content_ds_retweets_of_out_community_collection)

    def load_replies(self) -> Set[ContentSpaceTweet]:
        pass

    def load_time_stamps(self) -> List[datetime]:
        query = {"time_stamps": {"$exists": True}}
        return self.content_demand_supply_db[self.content_ds_curves] \
            .find_one(query)["time_stamps"]

    def load_curve(self, name: str) -> Dict[int, Dict[Any, Union[int,
                                            List[int]]]]:
        # load repr_to_num
        if len(repr_to_num) == 0:
            query = {"repr_to_num": {"$exists": True}}
            repr_to_num.update(self.content_demand_supply_db[self.content_ds_curves].find_one(query)["repr_to_num"])
        # get raw dictionary
        query = {name: {"$exists": True}}
        raw_dict = self.content_demand_supply_db[self.content_ds_curves].find_one(query)[name]
        # build new dictionary
        new_dict = {}
        for key1 in raw_dict.keys(): # userid
            new_sub_dict = {}
            for key2, value2 in raw_dict[key1].items(): # repr_num, time series
                new_sub_dict[repr_to_num[key2]] = value2
            new_dict[int(key1)] = new_sub_dict
        return new_dict

    def store_users(self, users: Set[ContentSpaceUser]) -> None:
        user_dict_list = []
        for user in users:
            user_dict = deepcopy(vars(user))
            user_dict["original_tweets"] = _serialize_space_tweet(
                user_dict["original_tweets"])
            user_dict["retweets_of_in_community"] = _serialize_space_tweet(
                user_dict["retweets_of_in_community"])
            user_dict["retweets_of_out_community"] = _serialize_space_tweet(
                user_dict["retweets_of_out_community"])
            user_dict["quotes_of_in_community"] = _serialize_space_tweet(
                user_dict["quotes_of_in_community"])
            user_dict["quotes_of_out_community"] = _serialize_space_tweet(
                user_dict["quotes_of_out_community"])
            user_dict["replies"] = _serialize_space_tweet(
                user_dict["replies"])
            user_dict_list.append(user_dict)
        self.content_demand_supply_db[self.content_ds_user_info].insert_many(
            user_dict_list)

    def store_tweets(self, tweets: Set[ContentSpaceTweet],
                     tweet_type: TweetType) -> None:
        if tweet_type == TweetType.ORIGINAL_TWEET:
            self.content_demand_supply_db[
                self.content_ds_original_tweets_collection] \
                .insert_many(_serialize_space_tweet(tweets))
        elif tweet_type == TweetType.RETWEET_OF_IN_COMM:
            self.content_demand_supply_db[
                self.content_ds_retweets_of_in_community_collection] \
                .insert_many(_serialize_space_tweet(tweets))
        elif tweet_type == TweetType.RETWEET_OF_OUT_COMM:
            self.content_demand_supply_db[
                self.content_ds_retweets_of_out_community_collection] \
                .insert_many(_serialize_space_tweet(tweets))
        else:
            raise ValueError

    def init_content_space(self, content_space_set: Set[ContentType]) -> None:
        content_space.update(content_space_set)

    def store_time_stamps(self, time_stamps: List[datetime]) -> None:
        self.content_demand_supply_db[self.content_ds_curves].insert_one({
            "time_stamps": time_stamps
        })

    def store_curve(self, curve: Dict[
                    str, Dict[int, Dict[Any, Union[int, List[int]]]]]) -> None:
        if len(repr_to_num) == 0:
            # create ContentType tracking
            repr_to_num.update(
                {str(index): content_type.representation for index,
                 content_type in enumerate(content_space)})
            self.content_demand_supply_db[self.content_ds_curves].insert_one({
                "repr_to_num": repr_to_num
            })
        curve_dict = self._subs_repr_to_num(curve)
        self.content_demand_supply_db[self.content_ds_curves] \
            .insert_one(curve_dict)

    def _subs_repr_to_num(self, curve: Dict[str, Dict[int, Dict[Any, Union[int,
                          List[int]]]]]) -> Dict[
                          str, Dict[str, Dict[str, Union[int, List[int]]]]]:
        new_dict = {}
        for key1 in curve.keys():  # name
            new_sub_dict = {}
            for key2, value2 in curve[key1].items():  # userid, Dict[Any, int]
                new_sub_dict[str(key2)] = self._sub_repr_to_num(value2)
            new_dict[key1] = new_sub_dict
        return new_dict

    def _sub_repr_to_num(self, small_dict: Dict[Any, Union[int, List[int]]]) -> \
            Dict[str, Union[int, List[int]]]:
        new_dict = {}
        for key, value in small_dict.items():
            new_dict[self._find_key_from_value(key)] = value
        return new_dict

    def _find_key_from_value(self, target_key: Any) -> str:
        for key, value in repr_to_num.items():
            if target_key == value:
                return key
