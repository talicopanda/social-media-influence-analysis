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


class SupplyCentricMATimeSeriesBuilder(TimeSeriesBuilderBase):
    """
    SupplyCentric + MA.
    """
    window: timedelta
    alpha: float

    supply_tweet_id_dict: Dict[int, List[int]]

    def __init__(self, ds: ContentDemandSupply, space: ContentSpace,
                 start: datetime, end: datetime, period: timedelta,
                 window: timedelta, alpha: float):
        self.ds = ds
        self.space = space
        self.time_stamps = []
        self._create_time_stamps(start, end, period)
        self.window = window
        self.alpha = alpha

        self.supply_tweet_id_dict = {}
        self._build_supply_id_dict()

    def _build_supply_id_dict(self) -> None:
        """Store original tweet's time index in self.supply_tweet_id_dict.
        """
        # Note: this assumes space contains all original tweets
        len_time = len(self.time_stamps)
        for tweet in self.space.original_tweets:
            ind_list = _find_time_index(tweet.created_at, self.time_stamps,
                                        len_time, self.window)
            self.supply_tweet_id_dict[tweet.id] = ind_list

    def create_time_series(self, user_type_or_id: Union[UserType, int],
                           content_repr: Any, mapping: str):
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError(f"Invalid Mapping Type {mapping}.")

        # compute supply
        if mapping == "supply":
            try:
                tweet_set = vars(self.ds)[mapping][user_type_or_id][
                    content_repr]
            except KeyError:
                tweet_set = set()

            output_list = [0] * len(self.time_stamps)

            # Generation
            for tweet in tweet_set:
                # calculate
                ind_list = self.supply_tweet_id_dict[tweet.id]

                # record
                for index in ind_list:
                    output_list[index] += 1
        # compute demand
        else:
            try:
                tweet_set = vars(self.ds)[mapping][user_type_or_id][
                    content_repr]
            except KeyError:
                tweet_set = set()

            output_list = np.zeros(len(self.time_stamps))
            time_array = np.array(self.time_stamps)

            for tweet in tweet_set:
                space_tweet = self.space.get_tweet(tweet.id)
                target_tweet_id = int(space_tweet.retweet_id)

                if target_tweet_id in self.supply_tweet_id_dict.keys():
                    # extract
                    ind_list = self.supply_tweet_id_dict[target_tweet_id]

                    # calculate
                    if len(ind_list) != 0:
                        retweet_time = tweet.created_at
                        times = time_array[ind_list]
                        deltas = retweet_time - times
                        discounts = np.exp(- self.alpha * deltas.astype('timedelta64[D]').astype(int))
                        output_list[ind_list] += np.clip(discounts, None, 1)
                else:
                    print(f"retweet {tweet.id}'s original tweet not found")
            # convert back to list
            output_list = output_list.tolist()

        # return result
        return output_list
