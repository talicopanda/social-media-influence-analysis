from typing import DefaultDict, List
from collections import defaultdict
from ContentMarketUser.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketClustering import ContentMarketClustering

class ContentMarketCoreNode(ContentMarketUser):
    demand_in_community: DefaultDict[int, List[int]]
    demand_out_of_community: DefaultDict[int, List[int]]
    aggregate_demand: DefaultDict[int, List[int]]
    supply: DefaultDict[int, List[int]]

    def __init__(self, **kwargs):
        self.demand_in_community = defaultdict(list)
        self.demand_out_of_community = defaultdict(list)
        self.aggregate_demand = defaultdict(list)
        self.supply = defaultdict(list)
        super().__init__(**kwargs)

    def calculate_demand(self, clustering: ContentMarketClustering):
        self.demand_in_community = self.build_support(self.retweets_of_in_community, clustering)
        self.demand_out_of_community = self.build_support(self.retweets_of_out_community, clustering)
        self.merge_support(self.aggregate_demand, self.demand_out_of_community)
        self.merge_support(self.aggregate_demand, self.demand_in_community)


    def calculate_supply(self, clustering: ContentMarketClustering):
        self.supply = self.build_support(self.original_tweets, clustering)
        quote_in_support = self.build_support(self.quotes_of_in_community, clustering)
        quote_out_support = self.build_support(self.quotes_of_out_community, clustering)
        self.merge_support(self.supply, quote_in_support)
        self.merge_support(self.supply, quote_out_support)
