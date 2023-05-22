from typing import List
from ContentMarketUser.ContentMarketConsumer import ContentMarketConsumer
from ContentMarketUser.ContentMarketProducer import ContentMarketProducer
from ContentMarketUser.ContentMarketCoreNode import ContentMarketCoreNode
from ContentMarket.ContentMarketClustering import ContentMarketClustering


class ContentMarket:
    """
    A class that represents the a content market and calculates information about
    users/tweets demands, supplies and causations
    """

    name: str
    consumers: List[ContentMarketConsumer]
    producers: List[ContentMarketProducer]
    core_nodes: List[ContentMarketCoreNode]
    clustering: ContentMarketClustering

    def __init__(self, name, consumers, producers, core_nodes, clustering):
        self.name = name
        self.consumers = consumers
        self.producers = producers
        self.core_nodes = core_nodes
        self.clustering = clustering


