from User.ContentMarketUser import ContentMarketUser
from Tweet.ContentMarketTweet import ContentMarketTweet

from Aggregation.AggregationBase import AggregationBase
from typing import Set


class ContentMarket(AggregationBase):
    """
    A class that represents the content market.
    """

    name: str
    consumers: Set[ContentMarketUser]
    producers: Set[ContentMarketUser]
    core_nodes: Set[ContentMarketUser]

    original_tweets: Set[ContentMarketTweet]
    retweets_of_in_comm: Set[ContentMarketTweet]
    retweets_of_out_comm: Set[ContentMarketTweet]
