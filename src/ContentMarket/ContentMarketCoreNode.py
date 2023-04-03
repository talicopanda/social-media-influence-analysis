from typing import DefaultDict, Tuple
from collections import defaultdict
from ContentMarket.ContentMarketUser import ContentMarketUser



class ContentMarketCoreNode(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here
    supply: DefaultDict

    def __init__(self, **kwargs):
        self.demand = defaultdict(list)
        self.supply = defaultdict(list)
        # self.calculate_demand(dao, retweets)
        # self.calculate_supply(dao, tweets, retweets_in_community)
        super().__init__(**kwargs)
    
    def calculate_demand(self, dao, retweets):
        pass

    def calculate_supply(self, dao, tweets, retweets_in_community):
        pass