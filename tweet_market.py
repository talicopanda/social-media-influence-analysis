from typing import List, Tuple
from tweet import Tweet, TweetContent, TweetType
from community import Community
import datetime


class TweetMarket:
    """
    A class that represents the tweet market and calculates information about
    users/tweets demands, correlations, etc.
    """

    tweets: List[Tweet]  # list of all
    community: Community

    def __init__(self):
        pass

    def demand(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        demand = 0
        for user_id in user_ids:
            user_tweets = get_tweets(user_id, time_range)  # db query
            for tweet in user_tweets:
                if tweet.type == TweetContent.TWEET and norm(tweet.content - content) < content_radius:
                    demand += 1
        return demand

    def avg_demand(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        return self.demand(content, content_radius, user_ids, time_range) / len(user_ids)

    def supply(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        supply = 0
        for user_id in user_ids:
            user_tweets = get_tweets(user_id, time_range)  # db query
            for tweet in user_tweets:
                if tweet.type == TweetContent.RETWEET and norm(tweet.content - content) < content_radius:
                    supply += 1
        return supply

    def avg_supply(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        return self.supply(content, content_radius, user_ids, time_range) / len(user_ids)

    # TODO: check if correlation calculation is even needed
    def correlation(self):
        pass

    # TODO: granger casuality
    def causation(self):
        pass
