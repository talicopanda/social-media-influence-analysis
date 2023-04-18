from __future__ import annotations

from typing import DefaultDict, List
from collections import defaultdict
from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketEmbedding import ContentMarketEmbedding
from ContentMarket.ContentMarketClustering import ContentMarketClustering


class ContentMarketProducer(ContentMarketUser):
    supply: DefaultDict[int, List[int]]

    def __init__(self, **kwargs):
        self.supply = defaultdict(list)
        super().__init__(**kwargs)

    def calculate_supply(self, clustering: ContentMarketClustering):
        self.supply = self.build_support(self.original_tweets, clustering)
        quote_in_support = self.build_support(self.quotes_of_in_community, clustering)
        quote_out_support = self.build_support(self.quotes_of_out_community, clustering)
        self.merge_support(self.supply, quote_in_support)
        self.merge_support(self.supply, quote_out_support)
