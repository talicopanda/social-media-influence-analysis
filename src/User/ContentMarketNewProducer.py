from __future__ import annotations

from typing import DefaultDict, List
import numpy as np
from collections import defaultdict
from User.ContentMarketUser import ContentMarketUser
import datetime

TIME_INT = datetime.timedelta(days=1)
R = 0.01
BATCH_SIZE = 10000


class ContentMarketNewProducer(ContentMarketUser):
    supply: DefaultDict[int, List[int]]

    def __init__(self, **kwargs):
        self.supply = defaultdict(list)
        super().__init__(**kwargs)

    def calculate_supply(self):
        # This is the version proposed in Further Discussion
        # find time interval
        tweet_times = np.array([tweet.created_at for tweet in self.original_tweets])
        min_time = tweet_times.min(initial=datetime.datetime.min)
        max_time = tweet_times.max(initial=datetime.datetime.max)


        # storing object
        time_stamps = []
        num_tweet = []

        # generate number of original tweets for each time interval
        curr_time = min_time
        while curr_time < max_time:
            time_stamps.append(curr_time)
            num_tweet.append(tweet_times[tweet_times >= curr_time & tweet_times < curr_time + TIME_INT])
            curr_time += TIME_INT
        # return pd.DataFrame(time=time_stamps, num_tweet=num_tweet)

        # This is another version proposed in Further Theory
        supply_series = {}
        for tweet in self.original_tweets:
            # storing object
            time_stamps = []
            num_tweet = []

            # iterate and get time series
            curr_time = min_time
            while curr_time < max_time:
                time_stamps.append(curr_time)
                num_tweet.append(self.get_close_tweet_num(tweet.id, curr_time,
                                                          curr_time + TIME_INT))
                curr_time += TIME_INT
            # save data
            if "time_stamp" not in supply_series.keys():
                supply_series["time_stamp"] = time_stamps
            supply_series[tweet.id] = num_tweet

    def get_close_tweet_num(self, tweet_id: int, start_time: datetime.datetime,
                            end_time: datetime.datetime,
                            threshold: float = R) -> int:
        pass
        # there are some Memory Array Error since the tweet_embedding data is so
        # large, if directly access to all data available; I will develop another
        # way of accessing data in batchs and calculate the supply

        # this method can also be used in Demand function
