from __future__ import annotations
# TODO: try to remove this import

from User.ContentMarketUser import ContentMarketUser
from Clustering.ContentMarketClustering import ContentMarketClustering
from Tweet.ContentMarketTweet import ContentMarketTweet

from typing import DefaultDict, Set, Any
from collections import defaultdict


class ContentMarketProducer(ContentMarketUser):
    supply: DefaultDict[Any, Set[ContentMarketTweet]]

    def __init__(self, **kwargs):
        self.supply = defaultdict(set)
        super().__init__(**kwargs)

    def calculate_supply(self, clustering: ContentMarketClustering):
        self.supply = self.build_support(self.original_tweets, clustering)
        quote_in_support = self.build_support(self.quotes_of_in_community, clustering)
        quote_out_support = self.build_support(self.quotes_of_out_community, clustering)
        self.merge_support(self.supply, quote_in_support)
        self.merge_support(self.supply, quote_out_support)
