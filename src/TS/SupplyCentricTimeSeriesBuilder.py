from TS.TimeSeriesBuilderBase import TimeSeriesBuilderBase
from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType
from Aggregation.ContentSpace import ContentSpace

from typing import List, Any, Union, Dict
from datetime import datetime, timedelta
from math import exp


def _find_time_index(create_time: datetime,
                     time_stamps: List[datetime], len_time: int) -> int:
    """Return -1 if not in the range.
    """
    for i in range(len_time):
        if create_time < time_stamps[i]:
            return i - 1
    return -1


class SupplyCentricTimeSeriesBuilder(TimeSeriesBuilderBase):
    """
    Count the retweets at the time stamp as its original tweet.
    """
    alpha: float

    supply_tweet_id_dict: Dict[int, int]

    def __init__(self, ds: ContentDemandSupply, space: ContentSpace,
                 start: datetime, end: datetime, period: timedelta,
                 alpha: float):
        self.ds = ds
        self.space = space
        self.time_stamps = []
        self._create_time_stamps(start, end, period)
        self.alpha = alpha

        self.supply_tweet_id_dict = {}
        self._build_supply_id_dict()

    def get_time_stamps(self) -> List[datetime]:
        return self.time_stamps[:-1]

    def _build_supply_id_dict(self) -> None:
        """Store original tweet's time index in self.supply_tweet_id_dict.
        """
        # Note: this assumes space contains all original tweets
        len_time = len(self.time_stamps)
        for tweet in self.space.original_tweets:
            ind = _find_time_index(tweet.created_at, self.time_stamps,
                                   len_time)
            self.supply_tweet_id_dict[tweet.id] = ind

    def create_time_series(self, user_type_or_id: Union[UserType, int],
                           content_repr: Any, mapping: str):
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError(f"Invalid Mapping Type {mapping}.")

        # compute supply
        if mapping == "supply":
            try:
                tweet_set = vars(self.ds)[mapping][user_type_or_id][content_repr]
            except KeyError:
                tweet_set = set()

            output_list = [0] * (len(self.time_stamps) - 1)

            # Generation
            for tweet in tweet_set:
                # calculate
                ind = self.supply_tweet_id_dict[tweet.id]

                # record
                if ind != -1:
                    output_list[ind] += 1
        # compute demand
        else:
            try:
                tweet_set = vars(self.ds)[mapping][user_type_or_id][content_repr]
            except KeyError:
                tweet_set = set()

            output_list = [0] * (len(self.time_stamps) - 1)

            for tweet in tweet_set:
                space_tweet = self.space.get_tweet(tweet.id)
                target_tweet_id = int(space_tweet.retweet_id)

                if target_tweet_id in self.supply_tweet_id_dict.keys():
                    # extract
                    ind = self.supply_tweet_id_dict[target_tweet_id]

                    # calculate
                    if ind != -1:
                        retweet_time = tweet.created_at
                        tweet_time = self.time_stamps[ind]
                        delta_days = (retweet_time - tweet_time).days
                        discount = exp(- self.alpha * delta_days)
                        output_list[ind] += min(discount, 1)
                else:
                    print(f"retweet {tweet.id}'s original tweet not found")

        # return result
        return output_list
