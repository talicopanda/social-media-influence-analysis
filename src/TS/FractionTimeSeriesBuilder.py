from TS.TimeSeriesBuilderBase import TimeSeriesBuilderBase
from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType
from Aggregation.ContentSpace import ContentSpace

from typing import List, Any, Union, Dict
from datetime import datetime, timedelta
import numpy as np


def _find_time_index(create_time: datetime,
                     time_stamps: List[datetime], len_time: int,
                     window: timedelta) -> List[int]:
    """Return empty list if not in the range.

    Precondition: time_stamps is sorted
    """
    # Note: rewrite for moving average
    ind_list = []

    lb = create_time - window
    ub = create_time + window

    for i in range(len_time):
        # Note: using enumerate() won't speed up the calculation
        curr_time = time_stamps[i]
        # sliding window
        if lb < curr_time < ub:
            ind_list.append(i)
        if curr_time > ub:
            return ind_list
    return ind_list


class FractionTimeSeriesBuilder(TimeSeriesBuilderBase):
    """
    Return the fraction of a content_type it occupies in the content space.

    Note: this class is no longer used
    """
    ds: ContentDemandSupply

    window: timedelta

    demand: Dict[Union[UserType, int], Dict[Any, List[float]]]
    supply: Dict[Union[UserType, int], Dict[Any, List[float]]]

    agg_demand: Dict[Any, List[int]]
    agg_supply: Dict[Any, List[int]]

    def __init__(self, ds: ContentDemandSupply, space: ContentSpace,
                 start: datetime, end: datetime, period: timedelta,
                 window: timedelta):
        self.ds = ds
        self.space = space
        self.time_stamps = []
        self._create_time_stamps(start, end, period)
        self.window = window

        self.demand = {}
        self.supply = {}
        self.agg_demand = {}
        self.agg_supply = {}

    def create_time_series(self, user_type_or_id: Union[UserType, int],
                           content_repr: Any, mapping: str) -> List[float]:
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError("Invalid Mapping Type.")

        # If already compute, simply return
        if mapping == "demand_in_community" and user_type_or_id in self.demand.keys():
            return self.demand[user_type_or_id][content_repr]
        elif mapping == "supply" and user_type_or_id in self.supply.keys():
            return self.supply[user_type_or_id][content_repr]
        # Else, start the computation
        else:
            # 1. initialize demand or supply
            if mapping == "demand_in_community":
                self.demand[user_type_or_id] = {}
            elif mapping == "supply":
                self.supply[user_type_or_id] = {}

            # 2. calculate the original time series
            original_dict = {}
            len_time = len(self.time_stamps)

            for content_type_repr in self.space.get_all_content_type_repr():
                try:
                    tweet_set = vars(self.ds)[mapping][user_type_or_id][content_type_repr]
                except KeyError:
                    tweet_set = set()

                output_list = np.zeros(len_time)

                # Generation
                for tweet in tweet_set:
                    # calculate
                    ind_list = _find_time_index(tweet.created_at, self.time_stamps,
                                                len_time, self.window)
                    # record
                    for index in ind_list:
                        output_list[index] += 1
                original_dict[content_type_repr] = output_list

            # 3. compute the fraction
            # step 1: compute the denominator
            sums = np.zeros(len_time)
            for value in original_dict.values():
                sums += value
            # if entry are zero, set it to be 1 to avoid Division by Zero
            sums[sums == 0] = 1

            # step 2: compute the fraction and store
            for content_type_repr in self.space.get_all_content_type_repr():
                if mapping == "demand_in_community":
                    self.demand[user_type_or_id][content_type_repr] = \
                        (original_dict[content_type_repr] / sums).tolist()
                elif mapping == "supply":
                    self.supply[user_type_or_id][content_type_repr] = \
                        (original_dict[content_type_repr] / sums).tolist()

            # 4. Return the desired list
            if mapping == "demand_in_community":
                return self.demand[user_type_or_id][content_repr]
            elif mapping == "supply":
                return self.supply[user_type_or_id][content_repr]

    def create_agg_time_series(self, content_repr: Any, mapping: str) -> List[float]:
        """Rewrite for fraction calculation.
        """
        # if already computed, then return
        if mapping == "demand_in_community" and content_repr in self.agg_demand.keys():
            return self.agg_demand[content_repr]
        elif mapping == "supply" and content_repr in self.agg_supply.keys():
            return self.agg_supply[content_repr]

        # else, start computation
        original_dict = {}
        len_time = len(self.time_stamps)

        for content_type_repr in self.space.get_all_content_type_repr():
            # get tweets
            tweet_set = None
            if mapping == "demand_in_community":
                tweet_set = vars(self.ds)[mapping][UserType.CONSUMER][content_type_repr]
            elif mapping == "supply":
                tweet_set = vars(self.ds)[mapping][UserType.PRODUCER][content_type_repr]
            tweet_set = tweet_set | vars(self.ds)[mapping][UserType.CORE_NODE][content_type_repr]

            # build integer time series
            output_list = np.zeros(len_time)

            for tweet in tweet_set:
                # calculate
                ind_list = _find_time_index(tweet.created_at, self.time_stamps,
                                            len_time, self.window)
                # record
                for index in ind_list:
                    output_list[index] += 1
            original_dict[content_type_repr] = output_list

        # convert to float
        sums = np.zeros(len_time)
        for value in original_dict.values():
            sums += value
        # if entry are zero, set it to be 1 to avoid Division by Zero
        sums[sums == 0] = 1

        # compute the fraction and store
        for content_type_repr in self.space.get_all_content_type_repr():
            if mapping == "demand_in_community":
                self.agg_demand[content_type_repr] = \
                    (original_dict[content_type_repr] / sums).tolist()
            elif mapping == "supply":
                self.agg_supply[content_type_repr] = \
                    (original_dict[content_type_repr] / sums).tolist()

        # Return the desired list
        if mapping == "demand_in_community":
            return self.agg_demand[content_repr]
        elif mapping == "supply":
            return self.agg_supply[content_repr]
