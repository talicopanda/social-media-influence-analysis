from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from Tweet.MinimalTweet import MinimalTweet
from Aggregation.ContentSpace import ContentSpace

from typing import List, Any, Union, Dict, DefaultDict, Set
from datetime import datetime, timedelta


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


class TimeSeriesBuilder:
    ds: ContentDemandSupply
    space: ContentSpace
    start: datetime
    end: datetime
    period: timedelta
    window: timedelta

    time_stamps: List[datetime]

    def __init__(self, *args):
        # param: ds: ContentDemandSupply, start: datetime, end: datetime, period: timedelta
        #        window: timedelta
        if len(args) == 5:
            self.ds = args[0]

            # create time stamps
            self.time_stamps = []
            self._create_time_stamps(args[1], args[2], args[3])
            self.window = args[4]

        # param: ds: ContentDemandSupply, space: ContentSpace start: datetime, end: datetime,
        #        period: timedelta, window: timedelta
        if len(args) == 6:
            self.ds = args[0]
            self.space = args[1]

            # create time stamps
            self.time_stamps = []
            self._create_time_stamps(args[2], args[3], args[4])
            self.window = args[5]

    def _create_time_stamps(self, start: datetime, end: datetime,
                            period: timedelta) -> None:
        """Create a list of time stamps for partitioning the Tweet, and
        store in self.time_stamps.
        """
        curr_time = start
        while curr_time <= end:
            self.time_stamps.append(curr_time)
            curr_time += period

    def create_time_series(self, user_type_or_id: Union[UserType, int],
                           content_repr: Any, mapping: str) -> List[int]:
        # Note: rewrite for moving average
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

    def create_type_series(self, user_type1: UserType, mapping1: str,
                           user_type2: UserType, mapping2: str,
                           content_repr: Any) -> (List[int], List[int]):
        demand_series = self.create_time_series(user_type1, content_repr,
                                                mapping1)
        supply_series = self.create_time_series(user_type2, content_repr,
                                                mapping2)
        return demand_series, supply_series

    def create_mapping_series(self, mapping: str) \
        -> List[Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]]]:
        """Creates a list of mappings. Each mapping in the list is restricted to the tweets that are
        in that time period."""
        # TODO: there is probably a better way to do this -- refactor.
        if mapping not in ["demand_in_community", "demand_out_community",
                           "supply"]:
            raise KeyError("Invalid Mapping Type.")
        print(f"==============Create {mapping.upper()} Series==============")

        import time
        start_time = time.time()
        temp1 = {}
        for user_type_or_id in vars(self.ds)[mapping]:
            temp2 = {}
            for content_type in self.ds.content_space:
                temp2[content_type.get_representation()] \
                    = self._partition_tweets_specific(user_type_or_id, content_type.get_representation(), mapping)
            temp1[user_type_or_id] = temp2
        print("Creation takes ", time.time() - start_time, " Seconds")

        start_time = time.time()
        len_time = len(self.time_stamps)
        mapping_series = [None] * len_time
        for i in range(len_time):
            mapping_dict = {}
            for user_type_or_id in vars(self.ds)[mapping]:
                content_dict = {}
                for content_type in self.ds.content_space:
                    content_dict[content_type.get_representation()] = temp1[user_type_or_id][content_type.get_representation()][i]
                mapping_dict[user_type_or_id] = content_dict
            mapping_series[i] = mapping_dict
        print("Transform takes ", time.time() - start_time, " Seconds")
        print(f"========Successfully Create {mapping.upper()} Series========")

        return mapping_series

    def partition_tweets_by_tweet_type(self, tweet_type: str) -> List[Set[ContentSpaceTweet]]:
        """Create a list of sets of tweets. Each set in the list is restricted to the tweets that
        are in that time period.
        <tweet_type> refers to either retweets_of_in_comm, retweets_of_out_comm, or original_tweets.
        """
        # TODO: refactor this to use the TweetType module?
        if tweet_type not in ["retweets_of_in_comm", "retweets_of_out_comm", "original_tweets"]:
            raise KeyError("Invalid Tweet Type.")

        len_time = len(self.time_stamps)
        partitioned_tweets = [set() for _ in range(len_time)]
        for tweet in vars(self.space)[tweet_type]:
            ind_list = _find_time_index(tweet.created_at, self.time_stamps,
                                        len_time, self.window)
            for index in ind_list:
                partitioned_tweets[index].add(tweet)

        return partitioned_tweets

    def _partition_tweets_specific(self, user_type_or_id: Union[UserType, int], content_repr: Any,
                                   mapping: str) -> List[Set[MinimalTweet]]:
        """Create a list of a sets of tweets. Each set in the list is restricted to the tweets that
        are in that time period, that have <user_type_or_id>, <content_repr>, and are a part of
        <mapping>.
        """
        if mapping not in ["demand_in_community", "demand_out_community", "supply"]:
            raise KeyError("Invalid Mapping Type.")

        # Extraction
        try:
            tweet_set = vars(self.ds)[mapping][user_type_or_id][content_repr]
        except KeyError:
            tweet_set = set()
        len_time = len(self.time_stamps)
        output_list = [set() for _ in range(len_time)]

        # Generation
        for tweet in tweet_set:
            ind_list = _find_time_index(tweet.created_at, self.time_stamps,
                                        len_time, self.window)
            for index in ind_list:
                output_list[index].add(tweet)

        return output_list
