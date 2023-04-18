from typing import DefaultDict, Tuple
from collections import defaultdict
from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketClustering import ContentMarketClustering

class ContentMarketCoreNode(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here
    supply: DefaultDict

    def __init__(self, **kwargs):
        self.demand = defaultdict(list)
        self.supply = defaultdict(list)
        super().__init__(**kwargs)
    
    def calculate_demand(self, clustering: ContentMarketClustering):
        self.demand = self.build_support(self.retweets_of_in_community, clustering)
        retweets_out = self.build_support(self.retweets_of_out_community, clustering)
        self.merge_support(self.demand, retweets_out)

    def calculate_supply(self, clustering: ContentMarketClustering):
        self.supply = self.build_support(self.original_tweets, clustering)
        quote_in_support = self.build_support(self.quotes_of_in_community, clustering)
        quote_out_support = self.build_support(self.quotes_of_out_community, clustering)
        self.merge_support(self.supply, quote_in_support)
        self.merge_support(self.supply, quote_out_support)
