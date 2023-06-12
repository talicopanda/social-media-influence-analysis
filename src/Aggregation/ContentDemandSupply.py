from User.UserManager import UserManager
from User.UserType import UserType
from Tweet.TweetType import TweetType
from Aggregation.AggregationBase import AggregationBase
from Mapping.ContentType import ContentType

from typing import Dict, List, Any, Set
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm


class ContentDemandSupply(AggregationBase):
    # Attributes
    name: str
    content_space: Set[ContentType]
    user_manager: UserManager

    time_stamps: List[datetime]

    user_demand: Dict[int, Dict[Any, List[int]]]
    user_supply: Dict[int, Dict[Any, List[int]]]
    user_agg_demand: Dict[int, Dict[Any, int]]
    user_agg_supply: Dict[int, Dict[Any, int]]

    def __init__(self, *args):
        # param: str, Set[ContentType], UserManager, TweetManager, timedelta
        if len(args) == 7:
            super().__init__(args[0], args[2], args[3])
            # load from arguments
            self.content_space = args[1]
            self.user_manager = args[2]
            start = args[4]
            end = args[5]
            period = args[6]
            self.time_stamps = []

            # create time stamps
            self._create_time_stamps(start, end, period)

            # initialize user demand and supply
            self.user_demand = {}
            self.user_supply = {}
            self.user_agg_demand = {}
            self.user_agg_supply = {}

            for user in self.user_manager.users:
                userid = user.user_id
                self.user_demand[userid] = {}
                self.user_supply[userid] = {}
                self.user_agg_demand[userid] = {}
                self.user_agg_supply[userid] = {}
        # param: str, UserManager, TweetManager, List[datetime],
        # Dict[int, Dict[Any, List[int]]], Dict[int, Dict[Any, List[int]]],
        # Dict[int, Dict[Any, int]], Dict[int, Dict[Any, int]]
        elif len(args) == 8:
            self.user_manager = args[1]
            super().__init__(args[0], args[1], args[2])
            self.time_stamps = args[3]
            self.user_demand = args[4]
            self.user_supply = args[5]
            self.user_agg_demand = args[6]
            self.user_agg_supply = args[7]
            self._create_content_space_from_tweet()

    def _create_time_stamps(self, start: datetime, end: datetime,
                            period: timedelta) -> None:
        """Create a list of time stamps for partitioning the Tweet, and
        store in self.time_stamps.
        """
        # TODO: automate min and max time
        curr_time = start
        while curr_time <= end:
            self.time_stamps.append(curr_time)
            curr_time += period

    def _create_content_space_from_tweet(self) -> None:
        content_space = []
        content_space.extend([tweet.content for tweet in self.original_tweets])
        content_space.extend([tweet.content for tweet in self.retweets_of_in_comm])
        content_space.extend([tweet.content for tweet in self.retweets_of_out_comm])
        self.content_space = set(content_space)

    def clear_trailing_zero(self) -> None:
        # TODO: adapt new
        pass

    # Below are methods for extraction from outer space
    def get_type_demand_series(self, user_type: UserType) \
            -> (List[datetime], Dict[Any, List[int]]):
        """Return the demand time series for <user_type>.
        """
        # TODO
        pass

    def get_type_supply_series(self, user_type: UserType) \
            -> (List[datetime], Dict[Any, List[int]]):
        """Return the demand time series for <user_type>.
        """
        # TODO
        pass

    def get_agg_demand(self, user_type: UserType) -> Dict[Any, int]:
        """Return the aggregate demand dictionary for <user_type>.
        """
        # TODO
        pass

    def get_agg_supply(self, user_type: UserType) -> Dict[Any, int]:
        """Return the aggregate supply dictionary for <user_type>.
        """
        # TODO
        pass

    def get_agg_type_demand_series(self, user_type: UserType) -> np.array:
        demand_series = list(self.get_type_demand_series(user_type)[1].values())
        return np.array(demand_series).sum(axis=0)

    def get_agg_type_supply_series(self, user_type: UserType) -> np.array:
        supply_series = list(self.get_type_supply_series(user_type)[1].values())
        return np.array(supply_series).sum(axis=0)

    def get_content_type_repr(self) -> List:
        return [content_type.get_representation() for content_type
                in self.content_space]

    ##########################################################
    # Test Version
    ##########################################################
    def _calculate_user_type_mapping(self, user_type: UserType,
                                     storage: Dict[int, Dict[Any, List[int]]],
                                     tweet_types: List[TweetType]) -> None:
        for user in tqdm(self.user_manager.get_type_users(user_type)):
            # ignore this type warning
            freq_dict = self.user_manager.calculate_user_time_mapping(
                user, self.time_stamps, tweet_types
            )
            storage[user.user_id] = freq_dict

    def calculate_user_demand(self):
        print("Start User Demand")
        demand_spec = [TweetType.RETWEET_OF_IN_COMM,
                       TweetType.RETWEET_OF_OUT_COMM]
        self._calculate_user_type_mapping(UserType.CONSUMER, self.user_demand,
                                          demand_spec)
        self._calculate_user_type_mapping(UserType.CORE_NODE, self.user_demand,
                                          demand_spec)

    def calculate_user_supply(self):
        print("Start User Supply")
        supply_spec = [TweetType.ORIGINAL_TWEET]
        self._calculate_user_type_mapping(UserType.PRODUCER, self.user_supply,
                                          supply_spec)
        self._calculate_user_type_mapping(UserType.CORE_NODE, self.user_supply,
                                          supply_spec)

    def calculate_user_agg_mapping(self):
        print("Start Agg Mapping")
        # demand
        for userid, freq_dict in self.user_demand.items():
            for content, time_series in freq_dict.items():
                self.user_agg_demand[userid][content] = sum(time_series)

        # supply
        for userid, freq_dict in self.user_supply.items():
            for content, time_series in freq_dict.items():
                self.user_agg_supply[userid][content] = sum(time_series)
