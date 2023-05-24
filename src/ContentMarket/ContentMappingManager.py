from ContentSpace.ContentSpace import ContentSpace
from User.ContentMarketUserManager import ContentMarketUserManager
from Tweet.ContentMarketTweetManager import ContentMarketTweetManager
from User.UserType import UserType, get_all_user_types
from Tweet.TweetType import TweetType

from typing import Dict, List, Any
from datetime import datetime, timedelta
from tqdm import trange


class ContentMappingManager:
    # Attributes
    content_space: ContentSpace
    user_manager: ContentMarketUserManager
    tweet_manager: ContentMarketTweetManager
    period: timedelta

    time_stamps: List[datetime]
    type_demand: Dict[UserType, Dict[Any, List[int]]]
    type_supply: Dict[UserType, Dict[Any, List[int]]]
    agg_demand: Dict[UserType, Dict[Any, int]]
    agg_supply: Dict[UserType, Dict[Any, int]]

    def __init__(self, content_space: ContentSpace,
                 user_manager: ContentMarketUserManager,
                 tweet_manager: ContentMarketTweetManager,
                 period: timedelta):
        # load from arguments
        self.content_space = content_space
        self.user_manager = user_manager
        self.tweet_manager = tweet_manager
        self.period = period
        self.time_stamps = []

        # create time stamps
        self._create_time_stamps()

        # initialize supply and demand variable
        self.type_demand = {}
        self.type_supply = {}
        self.agg_demand = {}
        self.agg_supply = {}

        # initialize first layer
        for user_type in get_all_user_types():
            self.type_demand[user_type] = {}
            self.type_supply[user_type] = {}
            self.agg_demand[user_type] = {}
            self.agg_supply[user_type] = {}

        # initialize second layer
        for user_type in get_all_user_types():
            for content_type in self.content_space.get_all_content_types():
                representation = content_type.get_representation()
                self.type_demand[user_type][representation] = []
                self.type_supply[user_type][representation] = []
                self.agg_demand[user_type][representation] = 0
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

    def _calculate_type_mapping(self, storage: Dict[UserType, Dict[Any, List[int]]],
                                tweet_types: List[TweetType]) -> None:
        """A helper function to create Dictionary of time series with given
        <tweet_types>, and store in <storage>.
        """
        for user_type in get_all_user_types():
            for i in trange(len(self.time_stamps) - 1):
                start_time = self.time_stamps[i]
                end_time = self.time_stamps[i + 1]
                # get data
                freq_dict = self.user_manager.\
                    calculate_time_mapping(user_type,start_time,end_time,
                                           self.content_space.clustering,
                                           self.content_space, tweet_types,
                                           self.tweet_manager)
                # store data
                for representation, freq in freq_dict.items():
                    storage[user_type][representation].append(freq)

    def calculate_type_demand(self) -> None:
        """Calculate demand time series for each ContentType for each UserType
        and store in self.type_demand.
        """
        print("=================Calculate Type Demand=================")
        tweet_types = [TweetType.RETWEET_OF_IN_COMM,
                       TweetType.RETWEET_OF_OUT_COMM]
        self._calculate_type_mapping(self.type_demand, tweet_types)
        print("=============Successfully Calculate Type Demand=============")

    def calculate_type_supply(self) -> None:
        """Calculate supply time series for each ContentType for each UserType
        and store in self.type_supply.
        """
        print("=================Calculate Type Supply=================")
        tweet_types = [TweetType.ORIGINAL_TWEET,
                       TweetType.QUOTE_OF_IN_COMM,
                       TweetType.QUOTE_OF_OUT_COMM]
        self._calculate_type_mapping(self.type_supply, tweet_types)
        print("=============Successfully Calculate Type Supply=============")

    def calculate_agg_mapping(self):
        """Aggregate information in self.type_demand and self.type_supply,
        then store the results in self.agg_demand and self.agg_supply.
        """
        print("===============Calculate Aggregate Mapping===============")
        for user_type in get_all_user_types():
            for content_type in self.content_space.get_all_content_types():
                representation = content_type.get_representation()
                # demand
                self.agg_demand[user_type][representation] = sum(
                    self.type_demand[user_type][representation]
                )

                # supply
                self.agg_supply[user_type][representation] = sum(
                    self.type_supply[user_type][representation]
                )
        print("=========Successfully Calculate Aggregate Demand=========")

    # Below are methods for extraction from outer space
    def get_type_demand_series(self, user_type: UserType) \
            -> (List[datetime], Dict[Any, List[int]]):
        """Return the demand time series for <user_type>.
        """
        return self.time_stamps, self.type_demand[user_type]


