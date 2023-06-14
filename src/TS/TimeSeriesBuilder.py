from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType

from typing import List, Any
from datetime import datetime, timedelta


def _find_time_index(create_time: datetime,
                     time_stamps: List[datetime], len_time: int) -> int:
    """Return -1 if not in the range.
    """
    for i in range(len_time):
        if create_time < time_stamps[i]:
            return i - 1
    return -1


class TimeSeriesBuilder:
    ds: ContentDemandSupply
    start: datetime
    end: datetime
    period: timedelta

    time_stamps: List[datetime]

    def __init__(self, ds: ContentDemandSupply, start: datetime, end: datetime,
                 period: timedelta):
        self.ds = ds

        # create time stamps
        self.time_stamps = []
        self._create_time_stamps(start, end, period)

    def _create_time_stamps(self, start: datetime, end: datetime,
                            period: timedelta) -> None:
        """Create a list of time stamps for partitioning the Tweet, and
        store in self.time_stamps.
        """
        curr_time = start
        while curr_time <= end:
            self.time_stamps.append(curr_time)
            curr_time += period

    def create_time_series(self, user_type: UserType, content_repr: Any,
                           mapping: str) -> List[int]:
        if mapping != "demand" or mapping != "supply":
            raise KeyError("Invalid Mapping Type.")

        # Extraction
        tweet_set = vars(self.ds)[mapping][user_type][content_repr]
        len_time = len(self.time_stamps)
        output_list = [0] * len_time

        # Generation
        for tweet in tweet_set:
            output_list[_find_time_index(tweet.created_at, self.time_stamps,
                                         len_time)] += 1

        return output_list
