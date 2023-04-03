from typing import DefaultDict
from collections import defaultdict

from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketEmbedding import ContentMarketEmbedding

class ContentMarketConsumer(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here

    def __init__(self, **kwargs):
        self.demand = defaultdict(list)
        # self.calculate_demand(dao, retweets)
        super().__init__(**kwargs)
    
    def calculate_demand(self, dao, retweets):
        pass