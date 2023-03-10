from typing import List, Tuple
from ContentMarketConsumer import ContentMarketConsumer
from ContentMarketProducer import ContentMarketProducer
from ContentMarketCoreNode import ContentMarketCoreNode
from ContentMarketEmbedding import ContentMarketEmbedding
import datetime


class ContentMarket:
    """
    A class that represents the a content market and calculates information about
    users/tweets demands, supplies and causations
    """

    consumers: List[ContentMarketConsumer]
    producers: List[ContentMarketProducer]
    core_node: ContentMarketCoreNode
    embedding: ContentMarketEmbedding

    def __init__(self):
        self.consumers = []  # load
        self.producers = []  # load
        self.core_node = None  # load

    def calulate_demand(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        demand = 0
        for user_id in user_ids:
            user_tweets = get_tweets(user_id, time_range)  # db query
            for tweet in user_tweets:
                if tweet.type == TweetContent.TWEET and norm(tweet.content - content) < content_radius:
                    demand += 1
        return demand

    def avg_demand(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        return self.calculate_demand(content, content_radius, user_ids, time_range) / len(user_ids)

    def calculate_supply(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        supply = 0
        for user_id in user_ids:
            user_tweets = get_tweets(user_id, time_range)  # db query
            for tweet in user_tweets:
                if tweet.type == TweetContent.RETWEET and norm(tweet.content - content) < content_radius:
                    supply += 1
        return supply

    def avg_supply(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
        return self.supply(content, content_radius, user_ids, time_range) / len(user_ids)

    def calculate_causation(self):
        pass
