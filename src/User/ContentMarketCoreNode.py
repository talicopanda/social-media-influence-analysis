from User.ContentMarketUser import ContentMarketUser
from Clustering.ContentMarketClustering import ContentMarketClustering
from Tweet.ContentMarketTweet import ContentMarketTweet

from typing import DefaultDict, Any, Set
from collections import defaultdict


class ContentMarketCoreNode(ContentMarketUser):
    demand_in_community: DefaultDict[Any, Set[ContentMarketTweet]]
    demand_out_of_community: DefaultDict[Any, Set[ContentMarketTweet]]
    aggregate_demand: DefaultDict[Any, Set[ContentMarketTweet]]
    supply: DefaultDict[Any, Set[ContentMarketTweet]]

    def __init__(self, **kwargs):
        self.demand_in_community = defaultdict(set)
        self.demand_out_of_community = defaultdict(set)
        self.aggregate_demand = defaultdict(set)
        self.supply = defaultdict(set)
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
