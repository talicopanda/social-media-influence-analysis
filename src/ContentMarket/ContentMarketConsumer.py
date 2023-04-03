from typing import DefaultDict, List
from collections import defaultdict

from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketClustering import ContentMarketClustering

class ContentMarketConsumer(ContentMarketUser):
    demand: DefaultDict[int, List[int]]

    def __init__(self, **kwargs):
        self.demand = defaultdict(list)
        super().__init__(**kwargs)
    
    def calculate_demand(self, clustering: ContentMarketClustering):
        self.demand = self.build_support(self.retweets_of_in_community, clustering)
        retweets_out = self.build_support(self.retweets_of_out_community , clustering)
        self.merge_support(self.demand, retweets_out)