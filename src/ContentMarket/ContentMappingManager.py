from ContentSpace.ContentSpace import ContentSpace
from User.ContentMarketUserManager import ContentMarketUserManager
from User.UserType import UserType
from Tweet.TweetType import TweetType, get_tweet_type

from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np
from tqdm import tqdm


class ContentMappingManager:
    # Attributes
    content_space: ContentSpace
    user_manager: ContentMarketUserManager
    period: timedelta

    time_stamps: List[datetime]
    demand_spec: Dict[UserType, List[TweetType]]
    supply_spec: Dict[UserType, List[TweetType]]

    user_demand: Dict[int, Dict[Any, List[int]]]
    user_supply: Dict[int, Dict[Any, List[int]]]
    user_agg_demand: Dict[int, Dict[Any, int]]
    user_agg_supply: Dict[int, Dict[Any, int]]

    type_demand: Dict[UserType, Dict[Any, List[int]]]
    type_supply: Dict[UserType, Dict[Any, List[int]]]
    agg_demand: Dict[UserType, Dict[Any, int]]
    agg_supply: Dict[UserType, Dict[Any, int]]

    def __init__(self, content_space: ContentSpace,
                 user_manager: ContentMarketUserManager,
                 period: timedelta,
                 mapping_spec: Dict[str, Dict[str, List[str]]]):
        # load from arguments
        self.content_space = content_space
        self.user_manager = user_manager
        self.period = period
        self.time_stamps = []

        # create time stamps
        self._create_time_stamps()

        # extract supply and demand specification
        self.demand_spec = {}
        self.supply_spec = {}
        self._get_mapping_spec(mapping_spec)

        # initialize supply and demand variable
        self.type_demand = {}
        self.type_supply = {}
        self.agg_demand = {}
        self.agg_supply = {}

        # initialize DEMAND
        demand_user_type = [UserType.CONSUMER, UserType.CORE_NODE]
        # first layer
        for user_type in demand_user_type:
            self.type_demand[user_type] = {}
            self.agg_demand[user_type] = {}
        # second layer
        for user_type in demand_user_type:
            for content_type in self.content_space.get_all_content_types():
                representation = content_type.get_representation()
                self.type_demand[user_type][representation] = []
                self.agg_demand[user_type][representation] = 0

        # initialize SUPPLY
        supply_user_type = [UserType.PRODUCER, UserType.CORE_NODE]
        # first layer
        for user_type in supply_user_type:
            self.type_supply[user_type] = {}
            self.agg_supply[user_type] = {}
        # second layer
        for user_type in supply_user_type:
            for content_type in self.content_space.get_all_content_types():
                representation = content_type.get_representation()
                self.type_supply[user_type][representation] = []
                self.agg_supply[user_type][representation] = 0

        #############################################################
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

    def _create_time_stamps(self) -> None:
        """Create a list of time stamps for partitioning the Tweet, and
        store in self.time_stamps.
        """
        min_time = datetime(2020, 6, 29)
        end_time = datetime.now()
        curr_time = min_time
        while curr_time <= end_time:
            self.time_stamps.append(curr_time)
            curr_time += self.period

    def _get_mapping_spec(self, mapping_spec: Dict[str,
    Dict[str, List[str]]]) -> None:
        """Extract information from <mapping_spec> and store in class
        attributes.
        """
        # extract and store
        self.demand_spec[UserType.CONSUMER] = [get_tweet_type(tweet_str) for
                                               tweet_str in
                                               mapping_spec["consumer"][
                                                   "demand"]]
        self.demand_spec[UserType.CORE_NODE] = [get_tweet_type(tweet_str) for
                                                tweet_str in
                                                mapping_spec["core node"][
                                                    "demand"]]
        self.supply_spec[UserType.PRODUCER] = [get_tweet_type(tweet_str) for
                                               tweet_str in
                                               mapping_spec["producer"][
                                                   "supply"]]
        self.supply_spec[UserType.CORE_NODE] = [get_tweet_type(tweet_str) for
                                                tweet_str in
                                                mapping_spec["core node"][
                                                    "supply"]]

    def _calculate_type_mapping(self, user_type: UserType,
                                storage: Dict[UserType, Dict[Any, List[int]]],
                                tweet_types: List[TweetType]) -> None:
        """A helper function to create Dictionary of time series with given
        <tweet_types>, and store in <storage>.
        """
        # get data
        freq_dict = self.user_manager. \
            calculate_time_mapping(user_type, self.time_stamps,
                                   self.content_space, tweet_types)
        # store data
        storage[user_type] = freq_dict

    def calculate_type_demand(self) -> None:
        """Calculate demand time series for each ContentType for each UserType
        and store in self.type_demand.
        """
        print("=================Calculate Type Demand=================")
        self._calculate_type_mapping(UserType.CONSUMER, self.type_demand,
                                     self.demand_spec[UserType.CONSUMER])
        self._calculate_type_mapping(UserType.CORE_NODE, self.type_demand,
                                     self.demand_spec[UserType.CORE_NODE])
        print("=============Successfully Calculate Type Demand=============")

    def calculate_type_supply(self) -> None:
        """Calculate supply time series for each ContentType for each UserType
        and store in self.type_supply.
        """
        print("=================Calculate Type Supply=================")
        self._calculate_type_mapping(UserType.PRODUCER, self.type_supply,
                                     self.supply_spec[UserType.PRODUCER])
        self._calculate_type_mapping(UserType.CORE_NODE, self.type_supply,
                                     self.supply_spec[UserType.CORE_NODE])
        print("=============Successfully Calculate Type Supply=============")

    def clear_trailing_zero(self) -> None:
        i = len(self.time_stamps)
        while i > 0:
            i -= 1 # current time stamp index
            remove_last = True
            # check if the last element in demand are all 0
            for user_type in self.demand_spec.keys():
                if not remove_last:
                    break
                for content_type_repr in self.type_demand[user_type].keys():
                    if self.type_demand[user_type][content_type_repr][-1] != 0:
                        remove_last = False
                        break

            # check if the last element in demand are all 0
            for user_type in self.supply_spec.keys():
                if not remove_last:
                    break
                # check if the last element in demand is 0
                for content_type_repr in self.type_supply[user_type].keys():
                    if self.type_supply[user_type][content_type_repr][-1] != 0:
                        remove_last = False
                        break

            # if <remove_last> is True, remove last element in all list and
            # remove the last time stamp
            if remove_last:
                # remove demand
                for user_type in self.demand_spec.keys():
                    for content_type_repr in self.type_demand[user_type].keys():
                        self.type_demand[user_type][content_type_repr].pop()
                # remove supply
                for user_type in self.supply_spec.keys():
                    for content_type_repr in self.type_supply[user_type].keys():
                        self.type_supply[user_type][content_type_repr].pop()
                # remove time stamp
                self.time_stamps.pop()
            # else, there are some list that contains non-zero element, and the
            # removal function will stop
            else:
                return

    def calculate_agg_mapping(self):
        """Aggregate information in self.type_demand and self.type_supply,
        then store the results in self.agg_demand and self.agg_supply.
        """
        print("===============Calculate Aggregate Mapping===============")
        # Demand
        for user_type in self.agg_demand.keys():
            for content_type in self.content_space.get_all_content_types():
                representation = content_type.get_representation()
                # demand
                self.agg_demand[user_type][representation] = sum(
                    self.type_demand[user_type][representation]
                )
        print("=========Successfully Calculate Aggregate Demand=========")

        # Supply
        for user_type in self.agg_supply.keys():
            for content_type in self.content_space.get_all_content_types():
                representation = content_type.get_representation()
                # supply
                self.agg_supply[user_type][representation] = sum(
                    self.type_supply[user_type][representation]
                )
        print("=========Successfully Calculate Aggregate Supply=========")

    # Below are methods for extraction from outer space
    def get_type_demand_series(self, user_type: UserType) \
            -> (List[datetime], Dict[Any, List[int]]):
        """Return the demand time series for <user_type>.
        """
        return self.time_stamps, self.type_demand[user_type]

    def get_type_supply_series(self, user_type: UserType) \
            -> (List[datetime], Dict[Any, List[int]]):
        """Return the demand time series for <user_type>.
        """
        return self.time_stamps, self.type_supply[user_type]

    def get_agg_demand(self, user_type: UserType) -> Dict[Any, int]:
        """Return the aggregate demand dictionary for <user_type>.
        """
        return self.agg_demand[user_type]

    def get_agg_supply(self, user_type: UserType) -> Dict[Any, int]:
        """Return the aggregate supply dictionary for <user_type>.
        """
        return self.agg_supply[user_type]

    def get_agg_type_demand_series(self, user_type: UserType) -> np.array:
        demand_series = list(self.get_type_demand_series(user_type)[1].values())
        return np.array(demand_series).sum(axis=0)

    def get_agg_type_supply_series(self, user_type: UserType) -> np.array:
        supply_series = list(self.get_type_supply_series(user_type)[1].values())
        return np.array(supply_series).sum(axis=0)

    def get_content_type_repr(self) -> List:
        return [content_type.get_representation() for content_type
                in self.content_space.get_all_content_types()]

    ##########################################################
    # Test Version
    ##########################################################
    def calculate_user_type_mapping(self, user_type: UserType,
                                    storage: Dict[int, Dict[Any, List[int]]],
                                    tweet_types: List[TweetType]) -> None:
        for user in tqdm(self.user_manager.get_type_users(user_type)):
            freq_dict = self.user_manager.calculate_user_time_mapping(user, self.time_stamps,
                                                                      self.content_space, tweet_types)
            storage[user.user_id] = freq_dict

    def calculate_user_demand(self):
        print("Start User Demand")
        self.calculate_user_type_mapping(UserType.CONSUMER, self.user_demand,
                                         self.demand_spec[UserType.CONSUMER])
        self.calculate_user_type_mapping(UserType.CORE_NODE, self.user_demand,
                                         self.demand_spec[UserType.CORE_NODE])

    def calculate_user_supply(self):
        print("Start User Supply")
        self.calculate_user_type_mapping(UserType.PRODUCER, self.user_supply,
                                         self.supply_spec[UserType.PRODUCER])
        self.calculate_user_type_mapping(UserType.CORE_NODE, self.user_supply,
                                         self.supply_spec[UserType.CORE_NODE])

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
