from User.UserManager import UserManager
from User.UserType import UserType
from Tweet.TweetType import TweetType
from Aggregation.AggregationBase import AggregationBase
from Mapping.ContentType import ContentType
from Tweet.MinimalTweet import MinimalTweet
from User.ContentSpaceUser import ContentSpaceUser

from typing import Dict, List, Any, Set, DefaultDict, Union
from tqdm import tqdm
from collections import defaultdict
from datetime import datetime


def _merge_dicts(dict1: Dict[Any, Set[MinimalTweet]], dict2: Dict[Any,
                 Set[MinimalTweet]]) -> None:
    """Update dict1.
    """
    for key, value in dict2.items():
        dict1[key].update(value)


def _clear_by_time_helper(start: datetime, end: datetime, storage:
                          Dict[Union[UserType, int],
                          DefaultDict[Any, Set[MinimalTweet]]]) -> None:
    for user, map_dict in storage.items():
        for content_type, tweet_set in map_dict.items():
            new_set = {tweet for tweet in tweet_set if start <=
                       tweet.created_at < end}
            storage[user][content_type] = new_set


class ContentDemandSupply(AggregationBase):
    """Aggregate Supply and Demand Information for time series processing.
    """
    # Attributes
    name: str
    content_space: Set[ContentType]
    user_manager: UserManager

    demand_in_community: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]]
    demand_out_community: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]]
    supply: Dict[Any, DefaultDict[Union[UserType, int], Set[MinimalTweet]]]

    def __init__(self, *args):
        # create()
        # param: str, Set[ContentType], UserManager, TweetManager
        if len(args) == 4:
            super().__init__(args[0], args[2], args[3])
            # load from arguments
            self.content_space = args[1]
            self.user_manager = args[2]

            # initialize demand and supply
            self.demand_in_community = {UserType.CONSUMER: defaultdict(set),
                                        UserType.CORE_NODE: defaultdict(set)}
            for user in self.user_manager.users:
                self.demand_in_community[user.user_id] = defaultdict(set)
            self.demand_out_community = {UserType.CONSUMER: defaultdict(set),
                                         UserType.CORE_NODE: defaultdict(set)}
            for user in self.user_manager.users:
                self.demand_out_community[user.user_id] = defaultdict(set)
            self.supply = {UserType.CORE_NODE: defaultdict(set),
                           UserType.PRODUCER: defaultdict(set)}
            for user in self.user_manager.users:
                self.supply[user.user_id] = defaultdict(set)
        # load()
        # param: str, Set[ContentType],
        #        Dict[UserType, Dict[Any, Set[MinimalTweet]]],
        #        Dict[UserType, Dict[Any, Set[MinimalTweet]]]
        elif len(args) == 5:
            self.name = args[0]
            self.content_space = args[1]
            self.demand_in_community = args[2]
            self.demand_out_community = args[3]
            self.supply = args[4]

    def get_content_type_repr(self) -> List:
        return [content_type.get_representation() for content_type
                in self.content_space]

    def _calculate_user_type_mapping(self, user_type: UserType,
                                     storage: Dict[Any,
                                     Dict[Any, Set[MinimalTweet]]],
                                     tweet_types: List[TweetType]) -> None:
        for user in tqdm(self.user_manager.get_type_users(user_type)):
            # ignore this type warning
            freq_dict = self.user_manager.calculate_user_time_mapping(
                user, tweet_types)
            _merge_dicts(storage[user_type], freq_dict)

    def _calculate_user_mapping(self, user: ContentSpaceUser,
                                storage: Dict[Any,
                                Dict[Any, Set[MinimalTweet]]],
                                tweet_types: List[TweetType]) -> None:
        freq_dict = self.user_manager.calculate_user_time_mapping(
                user, tweet_types)
        storage[user.user_id] = freq_dict

    def calculate_demand_in_community(self):
        print("Start User Demand In Community")
        demand_spec = [TweetType.RETWEET_OF_IN_COMM]
        self._calculate_user_type_mapping(UserType.CONSUMER, self.demand_in_community,
                                          demand_spec)
        self._calculate_user_type_mapping(UserType.CORE_NODE, self.demand_in_community,
                                          demand_spec)
        for user in self.user_manager.users:
            self._calculate_user_mapping(user, self.demand_in_community, demand_spec)

    def calculate_demand_out_community(self):
        print("Start User Demand Out Community")
        demand_spec = [TweetType.RETWEET_OF_OUT_COMM]
        self._calculate_user_type_mapping(UserType.CONSUMER, self.demand_out_community,
                                          demand_spec)
        self._calculate_user_type_mapping(UserType.CORE_NODE, self.demand_out_community,
                                          demand_spec)
        for user in self.user_manager.users:
            self._calculate_user_mapping(user, self.demand_out_community, demand_spec)

    def calculate_supply(self):
        print("Start User Supply")
        supply_spec = [TweetType.ORIGINAL_TWEET]
        self._calculate_user_type_mapping(UserType.PRODUCER, self.supply,
                                          supply_spec)
        self._calculate_user_type_mapping(UserType.CORE_NODE, self.supply,
                                          supply_spec)
        for user in self.user_manager.users:
            self._calculate_user_mapping(user, self.supply, supply_spec)

    def clear_tweets_by_time(self, start: datetime, end: datetime) -> None:
        _clear_by_time_helper(start, end, self.demand_in_community)
        _clear_by_time_helper(start, end, self.demand_out_community)
        _clear_by_time_helper(start, end, self.supply)
