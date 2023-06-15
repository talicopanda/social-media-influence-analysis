from DAO.MongoDAOBase import MongoDAOBase
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.TweetType import TweetType
from Mapping.ContentType import ContentType
from User.UserType import UserType, value_to_type
from Tweet.MinimalTweet import MinimalTweet

from typing import Set, List, Dict, Any, Union
from copy import deepcopy
from datetime import datetime

# file global variable
content_space = set()
num_to_repr = dict()


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
        pass

    def load_original_tweets(self) -> Set[ContentSpaceTweet]:
        pass

    def load_quotes_of_in_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_quotes_of_out_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_retweets_of_in_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_retweets_of_out_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_replies(self) -> Set[ContentSpaceTweet]:
        pass

    def load_content_space(self) -> set[ContentType]:
        # load num_to_repr
        if len(num_to_repr) == 0:
            query = {"num_to_repr": {"$exists": True}}
            num_to_repr.update(
                self.content_demand_supply_db[self.content_ds_content_space].find_one(
                    query)["num_to_repr"])
        # load Content Space
        content_space.clear()
        content_space.update({ContentType(type_repr) for type_repr
                              in num_to_repr.values()})
        return content_space

    def load_curve(self, name: str) -> Dict[Any, Dict[Any, Set[MinimalTweet]]]:
        # get raw dictionary
        query = {name: {"$exists": True}}
        raw_dict = self.content_demand_supply_db[self.content_ds_curves].find_one(query)[name]
        # build new dictionary
        new_dict = {}
        for key1 in raw_dict.keys(): # user_type
            new_sub_dict = {}
            for key2, value2 in raw_dict[key1].items():
                # key2 = repr_num, value2 = Set[tweet info]
                new_sub_dict[num_to_repr[key2]] = {MinimalTweet(**dct)
                                                   for dct in value2}
            new_dict[value_to_type(key1)] = new_sub_dict
        return new_dict

    def store_users(self, users: Set[ContentSpaceUser]) -> None:
        pass

    def store_tweets(self, tweets: Set[ContentSpaceTweet],
                     tweet_type: TweetType) -> None:
        pass

    def init_content_space(self, content_space_set: Set[ContentType]) -> None:
        content_space.update(content_space_set)

    def store_curve(self, name: str, curve: Dict[Any, Dict[Any,
                    Set[MinimalTweet]]]) -> None:
        if len(num_to_repr) == 0:
            # create ContentType tracking
            num_to_repr.update(
                {str(index): content_type.representation for index,
                 content_type in enumerate(content_space)})
            self.content_demand_supply_db[self.content_ds_content_space].insert_one(
                {"num_to_repr": num_to_repr}
            )
        curve_dict = self._subs_repr_to_num(curve)
        self.content_demand_supply_db[self.content_ds_curves] \
            .insert_one({name: curve_dict})

    def _subs_repr_to_num(self, curve: Dict[Any, Dict[Any, Set[MinimalTweet]]]) -> Dict[str, Dict[str, List[Dict[str, Union[int, datetime]]]]]:
        new_dict = {}
        for key, value in curve.items():
            # key = UserType, value = Dict[Any, Set[MinimalTweet]]
            new_sub_dict = self._sub_repr_to_num(value)
            new_sub_dict = self._min_tweet_to_dict(new_sub_dict)
            if type(key) is int:
                new_dict[str(key)] = new_sub_dict
            else:
                new_dict[key.value] = new_sub_dict
        return new_dict

    def _sub_repr_to_num(self, dct: Dict[Any, Set[MinimalTweet]]) -> \
            Dict[str, Set[MinimalTweet]]:
        new_dict = {}
        for key, value in dct.items():
            new_dict[self._find_key_from_value(key)] = value
        return new_dict

    def _find_key_from_value(self, target_key: Any) -> str:
        for key, value in num_to_repr.items():
            if target_key == value:
                return key

    def _min_tweet_to_dict(self, dct: Dict[str, Set[MinimalTweet]]) -> \
            Dict[str, List[Dict[str, Union[int, datetime]]]]:
        new_dict = {}
        for key, value in dct.items():
            tweet_dict_list = [{"id": tweet.id, "created_at": tweet.created_at}
                               for tweet in value]
            new_dict[key] = tweet_dict_list
        return new_dict
