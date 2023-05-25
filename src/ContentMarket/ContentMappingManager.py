from ContentSpace.ContentSpace import ContentSpace
from User.ContentMarketUserManager import ContentMarketUserManager
from User.UserType import UserType
from Tweet.TweetType import TweetType

from typing import Dict, List, Any
from datetime import datetime, timedelta


class ContentMappingManager:
    # Attributes
    content_space: ContentSpace
    user_manager: ContentMarketUserManager
    period: timedelta

    time_stamps: List[datetime]
    type_demand: Dict[UserType, Dict[Any, List[int]]]
    type_supply: Dict[UserType, Dict[Any, List[int]]]
    agg_demand: Dict[UserType, Dict[Any, int]]
    agg_supply: Dict[UserType, Dict[Any, int]]

    def __init__(self, content_space: ContentSpace,
                 user_manager: ContentMarketUserManager,
                 period: timedelta):
        # load from arguments
        self.content_space = content_space
        self.user_manager = user_manager
        self.period = period
        self.time_stamps = []

        # create time stamps
        self._create_time_stamps()

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

    def _calculate_type_mapping(self, user_type: UserType,
                                storage: Dict[UserType, Dict[Any, List[int]]],
                                tweet_types: List[TweetType]) -> None:
        """A helper function to create Dictionary of time series with given
        <tweet_types>, and store in <storage>.
        """
        # get data
        freq_dict = self.user_manager.\
            calculate_time_mapping(user_type, self.time_stamps,
                                   self.content_space, tweet_types)
        # store data
        storage[user_type] = freq_dict

    def calculate_type_demand(self) -> None:
        """Calculate demand time series for each ContentType for each UserType
        and store in self.type_demand.
        """
        print("=================Calculate Type Demand=================")
        tweet_types = [TweetType.RETWEET_OF_IN_COMM,
                       TweetType.RETWEET_OF_OUT_COMM]
        self._calculate_type_mapping(UserType.CONSUMER, self.type_demand, tweet_types)
        self._calculate_type_mapping(UserType.CORE_NODE, self.type_demand, tweet_types)
        print("=============Successfully Calculate Type Demand=============")

    def calculate_type_supply(self) -> None:
        """Calculate supply time series for each ContentType for each UserType
        and store in self.type_supply.
        """
        print("=================Calculate Type Supply=================")
        tweet_types = [TweetType.ORIGINAL_TWEET,
                       TweetType.QUOTE_OF_IN_COMM,
                       TweetType.QUOTE_OF_OUT_COMM]
        self._calculate_type_mapping(UserType.PRODUCER, self.type_supply, tweet_types)
        self._calculate_type_mapping(UserType.CORE_NODE, self.type_supply, tweet_types)
        print("=============Successfully Calculate Type Supply=============")

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
        return self.agg_supply[user_type]
