from __future__ import annotations

from typing import DefaultDict
from collections import defaultdict
from ContentMarket.ContentMarketUser import ContentMarketUser
from ContentMarket.ContentMarketEmbedding import ContentMarketEmbedding


class ContentMarketProducer(ContentMarketUser):
    supply: DefaultDict

    def __init__(self, **kwargs):
        self.supply = defaultdict(list)
        # self.calculate_supply(dao, tweets, retweets_in_community)
        super().__init__(**kwargs)

    def calculate_supply(self, dao, tweets, retweets_in_community):
        pass