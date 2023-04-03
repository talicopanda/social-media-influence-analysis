from typing import List, Tuple, Dict
from ContentMarket.ContentMarketConsumer import ContentMarketConsumer
from ContentMarket.ContentMarketProducer import ContentMarketProducer
from ContentMarket.ContentMarketCoreNode import ContentMarketCoreNode
from ContentMarket.ContentMarketClustering import ContentMarketClustering
from ContentMarket.ContentMarketUser import ContentMarketUser


class ContentMarket:
    """
    A class that represents the a content market and calculates information about
    users/tweets demands, supplies and causations
    """

    name: str
    consumers: List[ContentMarketConsumer]
    producers: List[ContentMarketProducer]
    core_nodes: List[ContentMarketCoreNode]
    computed_causations: List[float]

    def __init__(self, name, consumers, producers, core_nodes):
        self.name = name
        self.consumers = consumers
        self.producers = producers
        self.core_nodes = core_nodes
        self.computed_causations = []

    # def calulate_demand(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
    #     demand = 0
    #     for user_id in user_ids:
    #         user_tweets = get_tweets(user_id, time_range)  # db query
    #         for tweet in user_tweets:
    #             if tweet.type == TweetContent.TWEET and norm(tweet.content - content) < content_radius:
    #                 demand += 1
    #     return demand

    # def calculate_supply(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
    #     supply = 0
    #     for user_id in user_ids:
    #         user_tweets = get_tweets(user_id, time_range)  # db query
    #         for tweet in user_tweets:
    #             if tweet.type == TweetContent.RETWEET and norm(tweet.content - content) < content_radius:
    #                 supply += 1
    #     return supply

