from Aggregation.ContentDemandSupply import ContentDemandSupply
from Aggregation.ContentMarket import ContentMarket
from User.UserType import UserType
from Tweet.MinimalTweet import MinimalTweet

from typing import List, Any, Set
from datetime import datetime, timedelta


def _find_time_index(create_time: datetime,
                     time_stamps: List[datetime], len_time: int) -> int:
    """Return -1 if not in the range.
    """
    for i in range(len_time):
        if create_time < time_stamps[i]:
            return i - 1
    return -1


class WordTimeSeriesBuilder:
    market: ContentMarket
    ds: ContentDemandSupply
    start: datetime
    end: datetime
    period: timedelta

    time_stamps: List[datetime]

    def __init__(self, market: ContentMarket, ds: ContentDemandSupply,
                 start: datetime, end: datetime, period: timedelta):
        self.market = market
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
                           mapping: str, word_lst: List[str]) -> List[int]:
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError("Invalid Mapping Type.")

        # Extraction
        tweet_set = vars(self.ds)[mapping][user_type][content_repr]

        # Filter Tweets by word
        tweet_set = self._filter_by_words(tweet_set, word_lst)

        # Generation
        len_time = len(self.time_stamps)
        output_list = [0] * (len_time - 1)

        for tweet in tweet_set:
            index = _find_time_index(tweet.created_at, self.time_stamps,
                                     len_time)
            if index != -1:
                output_list[index] += 1

        return output_list

    def create_agg_time_series(self, user_type: UserType, mapping: str,
                               word_lst: List[str]) -> List[int]:
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError("Invalid Mapping Type.")

        # Extraction
        tweet_set_dict = vars(self.ds)[mapping][user_type]

        # Filter Tweets by word
        tweet_set = set()
        for tweet_repr_set in tweet_set_dict.values():
            tweet_set.update(self._filter_by_words(tweet_repr_set, word_lst))

        # Generation
        len_time = len(self.time_stamps)
        output_list = [0] * (len_time - 1)

        for tweet in tweet_set:
            index = _find_time_index(tweet.created_at, self.time_stamps,
                                     len_time)
            if index != -1:
                output_list[index] += 1

        return output_list

    def _filter_by_words(self, tweet_set: Set[MinimalTweet], word_lst:
                         List[str]) -> Set[MinimalTweet]:
        new_set = set()

        # get tweet content
        for tweet in tweet_set:
            content = self.market.get_content(tweet.id)

            # check if such tweet contains words in <word_lst>
            keep = False
            for word in word_lst:
                if word in content:
                    keep = True
                    break

            # store in new set
            if keep:
                new_set.add(tweet)

        return new_set
