from typing import List


class ContentMarketSupportEntry:
    """
    A class that stores info about a entry in a support function
    """

    center: List[float]
    tweet_ids: int
    furthest_tweet: int  # id
    furthest_tweet_dist: float
    closest_tweet: int  # id
    closest_tweet_dist: float

    def __init__(self, center, tweet_ids, furthest_tweet, furthest_tweet_dist, closest_tweet, closest_tweet_dist):
        self.center = center
        self.tweet_ids = tweet_ids
        self.furthest_tweet = furthest_tweet
        self.furthest_tweet_dist = furthest_tweet_dist
        self.closest_tweet = closest_tweet
        self.closest_tweet_dist = closest_tweet_dist
