from TS.TimeSeriesBuilderBase import TimeSeriesBuilderBase
from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType
from Aggregation.ContentSpace import ContentSpace

from typing import List, Any, Union
from datetime import datetime, timedelta


def _find_time_index(create_time: datetime, time_stamps: List[datetime],
                     len_time: int, window: timedelta) -> List[int]:
    """Return empty list if not in the range.

    Precondition: time_stamps is sorted
    """
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


class MATimeSeriesBuilder(TimeSeriesBuilderBase):
    """
    Count the tweet if the time stamps lies in
    [created_at - window, created_at + window].
    """
    window: timedelta

    def __init__(self, ds: ContentDemandSupply, space: ContentSpace,
                 start: datetime, end: datetime, period: timedelta,
                 window: timedelta):
        self.ds = ds
        self.space = space
        self.time_stamps = []
        self._create_time_stamps(start, end, period)
        self.window = window

    def create_time_series(self, user_type_or_id: Union[UserType, int],
                           content_repr: Any, mapping: str) -> List[int]:
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError("Invalid Mapping Type.")

        # Extraction
        try:
            tweet_set = vars(self.ds)[mapping][user_type_or_id][content_repr]
        except KeyError:
            tweet_set = set()
        len_time = len(self.time_stamps)
        output_list = [0] * len_time

        # Generation
        for tweet in tweet_set:
            # calculate
            ind_list = _find_time_index(tweet.created_at, self.time_stamps,
                                        len_time, self.window)
            # record
            for index in ind_list:
                output_list[index] += 1

        return output_list
